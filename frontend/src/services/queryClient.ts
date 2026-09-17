import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 30, // 30 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 0,
    },
  },
});

export async function apiRequest<T>(
  method: string,
  url: string,
  body?: unknown,
  options?: RequestInit
): Promise<Response> {
  const requestId = crypto.randomUUID();

  const headers: Record<string, string> = {
    'X-Request-ID': requestId,
    ...(options?.headers as Record<string, string>),
  };

  // Don't set Content-Type for FormData - let browser set it with boundary
  if (!(body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(url, {
    method,
    headers,
    body: body instanceof FormData ? body : body ? JSON.stringify(body) : undefined,
    credentials: 'include',
    ...options,
  });

  return response;
}