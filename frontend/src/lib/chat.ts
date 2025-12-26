/**
 * Chat API client functions
 */

import { api } from "./api";
import type { ChatRequest, ChatResponse } from "@/types/chat";

export async function sendMessage(
  message: string,
  conversationId?: string
): Promise<ChatResponse> {
  const requestData: ChatRequest = {
    message,
    conversation_id: conversationId,
  };

  return api.post<ChatResponse>("/api/chat", requestData);
}

export interface ChatHistoryResponse {
  conversation_id: string;
  messages: Array<{
    id: string;
    role: "user" | "assistant";
    content: string;
    created_at: string;
  }>;
}

export async function getChatHistory(
  conversationId: string
): Promise<ChatHistoryResponse> {
  return api.get<ChatHistoryResponse>(`/api/chat/history/${conversationId}`);
}

export interface ConversationsResponse {
  conversations: Array<{
    id: string;
    created_at: string;
    updated_at: string;
  }>;
}

export async function getUserConversations(): Promise<ConversationsResponse> {
  return api.get<ConversationsResponse>("/api/chat/conversations");
}
