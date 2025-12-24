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
