/**
 * Task API functions for use with TanStack Query.
 */

import { api } from './api';
import type { Task, TaskCreate, TaskUpdate, MessageResponse } from '@/types';

export async function getTasks(): Promise<Task[]> {
  return api.get<Task[]>('/api/tasks');
}

export async function createTask(data: TaskCreate): Promise<Task> {
  return api.post<Task>('/api/tasks', data);
}

export async function updateTask(taskId: number, data: TaskUpdate): Promise<Task> {
  return api.put<Task>(`/api/tasks/${taskId}`, data);
}

export async function deleteTask(taskId: number): Promise<MessageResponse> {
  return api.delete<MessageResponse>(`/api/tasks/${taskId}`);
}

export async function completeTask(taskId: number): Promise<Task> {
  return api.patch<Task>(`/api/tasks/${taskId}/complete`);
}
