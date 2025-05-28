import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

interface User {
  id: number
  username: string
  email: string
  full_name?: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (user: User, token: string) => void
  logout: () => void
  updateUser: (user: Partial<User>) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      
      login: (user: User, token: string) => {
        console.log('Login called with:', { user, token })
        set({
          user,
          token,
          isAuthenticated: true,
        })
      },
      
      logout: () => {
        console.log('Logout called')
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        })
      },
      
      updateUser: (userData: Partial<User>) => {
        const currentUser = get().user
        if (currentUser) {
          set({
            user: { ...currentUser, ...userData },
          })
        }
      },
    }),
    {
      name: 'email-client-auth',
      storage: createJSONStorage(() => localStorage),
    }
  )
)
