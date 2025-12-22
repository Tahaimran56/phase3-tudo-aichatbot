'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { TaskList } from '../../components/TaskList';
import { TaskForm } from '../../components/TaskForm';
import { getCurrentUser, signout, isApiError } from '../../lib/auth';
import { getTasks, createTask, updateTask, deleteTask, completeTask } from '../../lib/tasks';
import type { User } from '../../types';

export default function DashboardPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [user, setUser] = useState<User | null>(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [loadingTaskId, setLoadingTaskId] = useState<number | null>(null);

  // Check authentication
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const currentUser = await getCurrentUser();
        if (!currentUser) {
          router.push('/auth/signin');
          return;
        }
        setUser(currentUser);
      } catch {
        router.push('/auth/signin');
      } finally {
        setAuthLoading(false);
      }
    };
    checkAuth();
  }, [router]);

  // Fetch tasks
  const {
    data: tasks = [],
    isLoading: tasksLoading,
    error: tasksError,
  } = useQuery({
    queryKey: ['tasks'],
    queryFn: getTasks,
    enabled: !!user,
  });

  // Create task mutation
  const createMutation = useMutation({
    mutationFn: createTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });

  // Update task mutation
  const updateMutation = useMutation({
    mutationFn: ({ taskId, title }: { taskId: number; title: string }) =>
      updateTask(taskId, { title }),
    onMutate: ({ taskId }) => setLoadingTaskId(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
    onSettled: () => setLoadingTaskId(null),
  });

  // Delete task mutation
  const deleteMutation = useMutation({
    mutationFn: deleteTask,
    onMutate: (taskId) => setLoadingTaskId(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
    onSettled: () => setLoadingTaskId(null),
  });

  // Complete task mutation
  const completeMutation = useMutation({
    mutationFn: completeTask,
    onMutate: (taskId) => setLoadingTaskId(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
    onSettled: () => setLoadingTaskId(null),
  });

  // Handle sign out
  const handleSignout = async () => {
    try {
      await signout();
      router.push('/');
    } catch (error) {
      console.error('Signout error:', error);
    }
  };

  // Handle add task
  const handleAddTask = (title: string, description: string | null) => {
    createMutation.mutate({ title, description });
  };

  // Handle edit task
  const handleEditTask = (taskId: number, title: string) => {
    updateMutation.mutate({ taskId, title });
  };

  // Handle delete task
  const handleDeleteTask = (taskId: number) => {
    deleteMutation.mutate(taskId);
  };

  // Handle complete task
  const handleCompleteTask = (taskId: number) => {
    completeMutation.mutate(taskId);
  };

  // Loading state
  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
          <p className="mt-4 text-sm text-gray-500">Loading...</p>
        </div>
      </div>
    );
  }

  // Not authenticated
  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-4 py-4">
          <h1 className="text-xl font-semibold text-gray-900">My Tasks</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500">{user.email}</span>
            <button
              onClick={handleSignout}
              className="rounded-md bg-gray-100 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-200"
            >
              Sign Out
            </button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="mx-auto max-w-3xl px-4 py-8">
        {/* Error display */}
        {tasksError && (
          <div className="mb-6 rounded-lg bg-red-50 p-4">
            <p className="text-sm text-red-700">
              {isApiError(tasksError) ? tasksError.message : 'Failed to load tasks'}
            </p>
          </div>
        )}

        {/* Mutation error display */}
        {(createMutation.error || updateMutation.error || deleteMutation.error || completeMutation.error) && (
          <div className="mb-6 rounded-lg bg-red-50 p-4">
            <p className="text-sm text-red-700">
              An error occurred. Please try again.
            </p>
          </div>
        )}

        {/* Add task form */}
        <div className="mb-6">
          <TaskForm onSubmit={handleAddTask} isLoading={createMutation.isPending} />
        </div>

        {/* Task list */}
        <TaskList
          tasks={tasks}
          onComplete={handleCompleteTask}
          onEdit={handleEditTask}
          onDelete={handleDeleteTask}
          isLoading={tasksLoading}
          loadingTaskId={loadingTaskId}
        />
      </main>
    </div>
  );
}
