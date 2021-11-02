import { POST, request } from '../../request'

import type { ResponsePromise } from '../../request'
import type { HostConfig } from '../../types'
import type { Session } from '..'

export interface CreateCommandData {
  commandType: string
  data: Record<string, any>
}

export function createCommand(
  config: HostConfig,
  runId: string,
  data: CreateCommandData
): ResponsePromise<Session> {
  return request<Session, { data: CreateCommandData }>(
    POST,
    `/runs/${runId}/commands`,
    { data },
    config
  )
}