'use client';

import React, { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api-client';
import { TranslationTask, WorkerStatus } from '@/types/api';

export default function Dashboard() {
  const [tasks, setTasks] = useState<TranslationTask[]>([]);
  const [workers, setWorkers] = useState<WorkerStatus | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [tasksData, workersData] = await Promise.all([
        apiClient.getTasks(),
        apiClient.getWorkers(),
      ]);
      setTasks(tasksData);
      setWorkers(workersData);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000); // Polling every 10s
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="p-8">Loading TranslationTurbo Dashboard...</div>;

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <header className="flex justify-between items-center">
        <h1 className="text-3xl font-bold tracking-tight">Operator Dashboard</h1>
        <div className="flex space-x-4">
          <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
            Fleet Size: {workers?.count || 0} Workers
          </div>
          <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
            Mode: {workers?.mode || 'Quota-Saver'}
          </div>
        </div>
      </header>

      <section className="grid gap-4 md:grid-cols-3">
        <StatusCard title="Pending" count={tasks.filter(t => t.status === 'pending').length} color="bg-gray-100" />
        <StatusCard title="Processing" count={tasks.filter(t => t.status === 'processing').length} color="bg-yellow-100" />
        <StatusCard title="Completed" count={tasks.filter(t => t.status === 'completed').length} color="bg-green-100" />
      </section>

      <section className="bg-white border rounded-lg shadow-sm">
        <div className="p-4 border-b bg-gray-50 font-medium">Active Tasks</div>
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="text-sm text-gray-500 border-b">
              <th className="p-4">Task ID</th>
              <th className="p-4">Source URL</th>
              <th className="p-4">Language</th>
              <th className="p-4">Status</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map(task => (
              <tr key={task.id} className="border-b hover:bg-gray-50 transition-colors">
                <td className="p-4 text-sm font-mono">{task.id.slice(0, 8)}...</td>
                <td className="p-4 text-sm truncate max-w-xs">{task.source_url}</td>
                <td className="p-4 text-sm uppercase">{task.target_language}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${getStatusStyle(task.status)}`}>
                    {task.status}
                  </span>
                </td>
              </tr>
            ))}
            {tasks.length === 0 && (
              <tr>
                <td colSpan={4} className="p-8 text-center text-gray-500">No tasks found. Start by adding a YouTube URL.</td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </div>
  );
}

function StatusCard({ title, count, color }: { title: string; count: number; color: string }) {
  return (
    <div className={`p-6 rounded-xl border ${color}`}>
      <div className="text-sm font-medium text-gray-600">{title}</div>
      <div className="text-2xl font-bold">{count}</div>
    </div>
  );
}

function getStatusStyle(status: string) {
  switch (status) {
    case 'completed': return 'bg-green-100 text-green-700';
    case 'processing': return 'bg-yellow-100 text-yellow-700';
    case 'failed': return 'bg-red-100 text-red-700';
    case 'blocked': return 'bg-purple-100 text-purple-700';
    default: return 'bg-gray-100 text-gray-700';
  }
}
