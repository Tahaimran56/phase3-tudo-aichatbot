/**
 * Custom hook for chat state management
 */

import { useState, useEffect } from "react";
import { sendMessage as sendMessageApi, getChatHistory, getUserConversations } from "@/lib/chat";
import type { Message } from "@/types/chat";

export interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  conversationId: string | null;
  sendMessage: (message: string) => Promise<void>;
  clearError: () => void;
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);

  // Load conversation history on mount
  useEffect(() => {
    const loadHistory = async () => {
      try {
        const conversationsResponse = await getUserConversations();
        if (conversationsResponse.conversations.length > 0) {
          const latestConvId = conversationsResponse.conversations[0].id;
          setConversationId(latestConvId);
          const historyResponse = await getChatHistory(latestConvId);
          if (historyResponse.messages.length > 0) {
            const loadedMessages: Message[] = historyResponse.messages.map((msg) => ({
              id: msg.id,
              role: msg.role as "user" | "assistant",
              content: msg.content,
              created_at: msg.created_at,
            }));
            setMessages(loadedMessages);
          }
        }
      } catch {
        // Silent fail - user might not have any conversations yet
      }
    };
    loadHistory();
  }, []);

  const sendMessage = async (message: string) => {
    if (!message.trim()) return;

    setError(null);
    setIsLoading(true);

    // Add user message immediately for better UX
    const userMessage: Message = {
      id: "temp-" + new Date().getTime(),
      role: "user",
      content: message,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await sendMessageApi(message, conversationId || undefined);

      // Update conversation ID if this is first message
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      // Add assistant response
      const assistantMessage: Message = {
        id: new Date().getTime() + "-assistant",
        role: "assistant",
        content: response.response,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Failed to send message. Please try again.";
      setError(errorMessage);

      // Remove the user message that failed
      setMessages((prev) => prev.filter((m) => m.id !== userMessage.id));
    } finally {
      setIsLoading(false);
    }
  };

  const clearError = () => {
    setError(null);
  };

  return {
    messages,
    isLoading,
    error,
    conversationId,
    sendMessage,
    clearError,
  };
}
