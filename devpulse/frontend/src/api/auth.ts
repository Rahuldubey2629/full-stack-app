import { api } from '@/api/client'
import type { TokenResponse } from '@/types/auth'

export async function login(email: string, password: string): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>('/auth/login', { email, password })
  return data
}

export async function register(email: string, password: string): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>('/auth/register', { email, password })
  return data
}
