import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiService, EmailAccount, EmailAccountCreate } from '../services/api'
import { toast } from 'react-hot-toast'

// Query keys
export const accountKeys = {
  all: ['accounts'] as const,
  lists: () => [...accountKeys.all, 'list'] as const,
  details: () => [...accountKeys.all, 'detail'] as const,
  detail: (id: number) => [...accountKeys.details(), id] as const,
  folders: (id: number) => [...accountKeys.detail(id), 'folders'] as const,
}

// Get all email accounts
export function useEmailAccounts() {
  return useQuery({
    queryKey: accountKeys.lists(),
    queryFn: () => apiService.getEmailAccounts(),
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

// Create email account
export function useCreateEmailAccount() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (accountData: EmailAccountCreate) => apiService.createEmailAccount(accountData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: accountKeys.lists() })
      toast.success('Email account created successfully!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create email account')
    },
  })
}

// Update email account
export function useUpdateEmailAccount() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ accountId, accountData }: {
      accountId: number
      accountData: Partial<EmailAccountCreate>
    }) => apiService.updateEmailAccount(accountId, accountData),
    onSuccess: (updatedAccount) => {
      queryClient.invalidateQueries({ queryKey: accountKeys.lists() })
      queryClient.setQueryData(accountKeys.detail(updatedAccount.id), updatedAccount)
      toast.success('Account updated successfully!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update account')
    },
  })
}

// Delete email account
export function useDeleteEmailAccount() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (accountId: number) => apiService.deleteEmailAccount(accountId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: accountKeys.lists() })
      toast.success('Account deleted successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete account')
    },
  })
}

// Test email account connection
export function useTestEmailAccount() {
  return useMutation({
    mutationFn: (accountId: number) => apiService.testEmailAccount(accountId),
    onSuccess: (result) => {
      if (result.imap_success && result.smtp_success) {
        toast.success('Connection test successful!')
      } else {
        toast.error(result.error_message || 'Connection test failed')
      }
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Connection test failed')
    },
  })
}

// Upload avatar
export function useUploadAvatar() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ accountId, file }: { accountId: number; file: File }) =>
      apiService.uploadAvatar(accountId, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: accountKeys.lists() })
      toast.success('Avatar uploaded successfully!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to upload avatar')
    },
  })
}

// Get email folders
export function useEmailFolders(accountId: number, enabled = true) {
  return useQuery({
    queryKey: accountKeys.folders(accountId),
    queryFn: () => apiService.getEmailFolders(accountId),
    enabled,
    staleTime: 1000 * 60 * 10, // 10 minutes
  })
}
