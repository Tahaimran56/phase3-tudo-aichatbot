'use client';

import { useState } from 'react';
import type { Task } from '../types';

interface TaskItemProps {
  task: Task;
  onComplete: (taskId: number) => void;
  onEdit: (taskId: number, title: string) => void;
  onDelete: (taskId: number) => void;
  isLoading?: boolean;
}

export function TaskItem({
  task,
  onComplete,
  onEdit,
  onDelete,
  isLoading,
}: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const handleSaveEdit = () => {
    if (editTitle.trim() && editTitle !== task.title) {
      onEdit(task.id, editTitle.trim());
    }
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setEditTitle(task.title);
    setIsEditing(false);
  };

  const handleDelete = () => {
    onDelete(task.id);
    setShowDeleteConfirm(false);
  };

  return (
    <div
      className={`rounded-lg border bg-white p-4 shadow-sm transition-opacity ${
        isLoading ? 'opacity-50' : ''
      } ${task.is_completed ? 'border-green-200 bg-green-50' : 'border-gray-200'}`}
    >
      <div className="flex items-start gap-3">
        {/* Checkbox */}
        <button
          onClick={() => !task.is_completed && onComplete(task.id)}
          disabled={task.is_completed || isLoading}
          className={`mt-1 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded border-2 ${
            task.is_completed
              ? 'border-green-500 bg-green-500 text-white'
              : 'border-gray-300 hover:border-blue-500'
          }`}
          aria-label={task.is_completed ? 'Task completed' : 'Mark as complete'}
        >
          {task.is_completed && (
            <svg className="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                clipRule="evenodd"
              />
            </svg>
          )}
        </button>

        {/* Content */}
        <div className="min-w-0 flex-1">
          {isEditing ? (
            <div className="flex gap-2">
              <input
                type="text"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                className="flex-1 rounded border border-gray-300 px-2 py-1 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleSaveEdit();
                  if (e.key === 'Escape') handleCancelEdit();
                }}
              />
              <button
                onClick={handleSaveEdit}
                className="rounded bg-blue-600 px-3 py-1 text-sm text-white hover:bg-blue-700"
              >
                Save
              </button>
              <button
                onClick={handleCancelEdit}
                className="rounded bg-gray-200 px-3 py-1 text-sm text-gray-700 hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          ) : (
            <>
              <h3
                className={`text-sm font-medium ${
                  task.is_completed ? 'text-gray-500 line-through' : 'text-gray-900'
                }`}
              >
                {task.title}
              </h3>
              {task.description && (
                <p className="mt-1 text-sm text-gray-500">{task.description}</p>
              )}
            </>
          )}
        </div>

        {/* Actions */}
        {!isEditing && !showDeleteConfirm && (
          <div className="flex flex-shrink-0 gap-2">
            {!task.is_completed && (
              <button
                onClick={() => setIsEditing(true)}
                disabled={isLoading}
                className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
                aria-label="Edit task"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                  />
                </svg>
              </button>
            )}
            <button
              onClick={() => setShowDeleteConfirm(true)}
              disabled={isLoading}
              className="rounded p-1 text-gray-400 hover:bg-red-100 hover:text-red-600"
              aria-label="Delete task"
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          </div>
        )}

        {/* Delete confirmation */}
        {showDeleteConfirm && (
          <div className="flex flex-shrink-0 gap-2">
            <button
              onClick={handleDelete}
              disabled={isLoading}
              className="rounded bg-red-600 px-3 py-1 text-sm text-white hover:bg-red-700"
            >
              Delete
            </button>
            <button
              onClick={() => setShowDeleteConfirm(false)}
              className="rounded bg-gray-200 px-3 py-1 text-sm text-gray-700 hover:bg-gray-300"
            >
              Cancel
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
