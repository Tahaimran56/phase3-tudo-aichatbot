/**
 * TypeScript types for the Todo Web App.
 */

// User types
export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface SignupData {
  email: string;
  password: string;
}

export interface SigninData {
  email: string;
  password: string;
}

// Task types
export interface Task {
  id: number;
  title: string;
  description: string | null;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string | null;
}

export interface TaskUpdate {
  title: string;
}

// API Response types
export interface MessageResponse {
  message: string;
}

export interface ErrorResponse {
  error: string;
  message: string;
  status_code: number;
}
