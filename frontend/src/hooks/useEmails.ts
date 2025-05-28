import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiService, Email } from '../services/api'
import { toast } from 'react-hot-toast'

// Query keys
export const emailKeys = {
  all: ['emails'] as const,
  lists: () => [...emailKeys.all, 'list'] as const,
  list: (filters: Record<string, any>) => [...emailKeys.lists(), filters] as const,
  details: () => [...emailKeys.all, 'detail'] as const,
  detail: (id: number) => [...emailKeys.details(), id] as const,
}

// Get emails with filters
export function useEmails(params?: {
  account_id?: number
  folder?: string
  limit?: number
  offset?: number
}) {
  return useQuery({
    queryKey: emailKeys.list(params || {}),
    queryFn: () => apiService.getEmails(params),
    enabled: !!params?.account_id, // Only fetch if account is selected
    staleTime: 1000 * 60 * 2, // 2 minutes
    refetchOnWindowFocus: false,
  })
}

// Get single email
export function useEmail(emailId: number) {
  return useQuery({
    queryKey: emailKeys.detail(emailId),
    queryFn: () => apiService.getEmail(emailId),
    enabled: !!emailId,
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

// Update email (mark as read, star, etc.)
export function useUpdateEmail() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ emailId, updates }: {
      emailId: number
      updates: {
        is_read?: boolean
        is_starred?: boolean
        is_deleted?: boolean
        folder?: string
        labels?: string[]
      }
    }) => apiService.updateEmail(emailId, updates),
    onSuccess: (updatedEmail) => {
      // Update the email in cache
      queryClient.setQueryData(emailKeys.detail(updatedEmail.id), updatedEmail)
      
      // Invalidate email lists to refresh counts and status
      queryClient.invalidateQueries({ queryKey: emailKeys.lists() })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update email')
    },
  })
}

// Delete email
export function useDeleteEmail() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (emailId: number) => apiService.deleteEmail(emailId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: emailKeys.lists() })
      toast.success('Email deleted successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete email')
    },
  })
}

// Compose/Send email
export function useComposeEmail() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: apiService.composeEmail,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: emailKeys.lists() })
      toast.success('Email sent successfully!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to send email')
    },
  })
}

// Sync emails from server
export function useSyncEmails() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ accountId, folder = 'INBOX' }: { accountId: number; folder?: string }) =>
      apiService.syncEmails(accountId, folder),
    onSuccess: (result) => {
      // Invalidate all email queries to refresh the list
      queryClient.invalidateQueries({ queryKey: emailKeys.lists() })
      toast.success(result.message || 'Emails synced successfully!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to sync emails')
    },
  })
}

// Search emails
export function useSearchEmails() {
  return useMutation({
    mutationFn: (searchData: {
      query?: string
      folder?: string
      sender?: string
      subject?: string
      date_from?: string
      date_to?: string
      is_read?: boolean
      is_starred?: boolean
    }) => apiService.searchEmails(searchData),
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Search failed')
    },
  })
}
