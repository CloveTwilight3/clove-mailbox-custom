import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface EmailState {
  activeFolder: string
  selectedAccountId: number | null
  searchQuery: string
  selectedEmailId: number | null
  isComposing: boolean
  
  // Actions
  setActiveFolder: (folder: string) => void
  setSelectedAccountId: (accountId: number | null) => void
  setSearchQuery: (query: string) => void
  setSelectedEmailId: (emailId: number | null) => void
  setIsComposing: (isComposing: boolean) => void
}

export const useEmailStore = create<EmailState>()(
  persist(
    (set) => ({
      activeFolder: 'INBOX',
      selectedAccountId: null,
      searchQuery: '',
      selectedEmailId: null,
      isComposing: false,
      
      setActiveFolder: (folder: string) => set({ activeFolder: folder }),
      setSelectedAccountId: (accountId: number | null) => set({ selectedAccountId: accountId }),
      setSearchQuery: (query: string) => set({ searchQuery: query }),
      setSelectedEmailId: (emailId: number | null) => set({ selectedEmailId: emailId }),
      setIsComposing: (isComposing: boolean) => set({ isComposing }),
    }),
    {
      name: 'email-store',
      partialize: (state) => ({
        activeFolder: state.activeFolder,
        selectedAccountId: state.selectedAccountId,
      }),
    }
  )
)
