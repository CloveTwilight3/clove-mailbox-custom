import axios, { AxiosInstance, AxiosResponse } from 'axios'
import { useAuthStore } from '../stores/authStore'

// Types
export interface EmailAccount {
  id: number
  name: string
  email_address: string
  display_name?: string
  avatar_url?: string
  is_active: boolean
  is_default: boolean
  last_sync?: string
  created_at: string
  updated_at?: string
}

export interface EmailAccountCreate {
  name: string
  email_address: string
  display_name?: string
  imap_host: string
  imap_port: number
  imap_ssl: boolean
  imap_username: string
  imap_password: string
  smtp_host: string
  smtp_port: number
  smtp_ssl: boolean
  smtp_username: string
  smtp_password: string
  pop3_host?: string
  pop3_port?: number
  pop3_ssl?: boolean
  pop3_username?: string
  pop3_password?: string
}

export interface Email {
  id: number
  account_id: number
  message_id: string
  uid?: string
  subject?: string
  sender_name?: string
  sender_email: string
  reply_to?: string
  to_addresses?: Array<{ email: string; name?: string }>
  cc_addresses?: Array<{ email: string; name?: string }>
  bcc_addresses?: Array<{ email: string; name?: string }>
  body_text?: string
  body_html?: string
  attachments?: any[]
  date_sent?: string
  date_received?: string
  size?: number
  is_read: boolean
  is_starred: boolean
  is_deleted: boolean
  is_draft: boolean
  is_sent: boolean
  folder: string
  labels?: string[]
  created_at: string
  updated_at?: string
}

export interface EmailCompose {
  account_id: number
  to_addresses: Array<{ email: string; name?: string }>
  cc_addresses?: Array<{ email: string; name?: string }>
  bcc_addresses?: Array<{ email: string; name?: string }>
  subject: string
  body_text?: string
  body_html?: string
  attachments?: string[]
}

class ApiService {
  private api: AxiosInstance

  constructor() {
    this.api = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor to add auth token
    this.api.interceptors.request.use((config) => {
      const token = useAuthStore.getState().token
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    // Response interceptor to handle auth errors
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          useAuthStore.getState().logout()
        }
        return Promise.reject(error)
      }
    )
  }

  // Auth methods
  async login(username: string, password: string) {
    const response = await this.api.post('/api/v1/auth/login', {
      username,
      password,
    })
    return response.data
  }

  async register(userData: {
    username: string
    email: string
    password: string
    full_name?: string
  }) {
    const response = await this.api.post('/api/v1/auth/register', userData)
    return response.data
  }

  async getCurrentUser() {
    const response = await this.api.get('/api/v1/auth/me')
    return response.data
  }

  // Email Account methods
  async getEmailAccounts(): Promise<EmailAccount[]> {
    const response = await this.api.get('/api/v1/accounts/')
    return response.data
  }

  async createEmailAccount(accountData: EmailAccountCreate): Promise<EmailAccount> {
    const response = await this.api.post('/api/v1/accounts/', accountData)
    return response.data
  }

  async updateEmailAccount(accountId: number, accountData: Partial<EmailAccountCreate>): Promise<EmailAccount> {
    const response = await this.api.put(`/api/v1/accounts/${accountId}`, accountData)
    return response.data
  }

  async deleteEmailAccount(accountId: number): Promise<void> {
    await this.api.delete(`/api/v1/accounts/${accountId}`)
  }

  async testEmailAccount(accountId: number) {
    const response = await this.api.post(`/api/v1/accounts/${accountId}/test`)
    return response.data
  }

  async uploadAvatar(accountId: number, file: File) {
    const formData = new FormData()
    formData.append('file', file)
    const response = await this.api.post(`/api/v1/accounts/${accountId}/avatar`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  }

  async getEmailFolders(accountId: number) {
    const response = await this.api.get(`/api/v1/accounts/${accountId}/folders`)
    return response.data
  }

  // Email methods
  async getEmails(params?: {
    account_id?: number
    folder?: string
    limit?: number
    offset?: number
  }): Promise<Email[]> {
    const response = await this.api.get('/api/v1/emails/', { params })
    return response.data
  }

  async getEmail(emailId: number): Promise<Email> {
    const response = await this.api.get(`/api/v1/emails/${emailId}`)
    return response.data
  }

  async updateEmail(emailId: number, updates: {
    is_read?: boolean
    is_starred?: boolean
    is_deleted?: boolean
    folder?: string
    labels?: string[]
  }): Promise<Email> {
    const response = await this.api.put(`/api/v1/emails/${emailId}`, updates)
    return response.data
  }

  async deleteEmail(emailId: number): Promise<void> {
    await this.api.delete(`/api/v1/emails/${emailId}`)
  }

  async composeEmail(emailData: EmailCompose): Promise<void> {
    await this.api.post('/api/v1/emails/compose', emailData)
  }

  async syncEmails(accountId: number, folder = 'INBOX') {
    const response = await this.api.post(`/api/v1/emails/sync/${accountId}`, null, {
      params: { folder }
    })
    return response.data
  }

  async searchEmails(searchData: {
    query?: string
    folder?: string
    sender?: string
    subject?: string
    date_from?: string
    date_to?: string
    is_read?: boolean
    is_starred?: boolean
  }): Promise<Email[]> {
    const response = await this.api.post('/api/v1/emails/search', searchData)
    return response.data
  }
}

export const apiService = new ApiService()
