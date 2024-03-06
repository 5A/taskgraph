import { storeToRefs } from 'pinia'
import { RestfulStatus, useConnectionInfoStore, useConnectionStatusStore } from '@/store/connection'
import { useTokenStore } from '@/store/authentication'

export async function callRESTfulAPI(
  path: string,
  method: string,
  body: string | null = null,
  query: Record<string, string> | null = null
) {
  // Because we are using Pinia outside of a Vue component, we need to import the stores inside the function.
  // This makes sure that pinia instance is initialized and loaded by the app before calling useStore.
  // There's some performance overhead here though, but since we are already using js, performance is not a big deal.
  // see https://github.com/vuejs/pinia/discussions/687#discussioncomment-1374812
  const tokenStore = useTokenStore()
  const connInfoStore = useConnectionInfoStore()
  const { restful_endpoint } = storeToRefs(connInfoStore)
  const connStatusStore = useConnectionStatusStore()
  const target_url = query
    ? restful_endpoint.value + path + '?' + new URLSearchParams(query)
    : restful_endpoint.value + path
  try {
    const response = await fetch(target_url, {
      method: method,
      body: body,
      headers: {
        'Content-Type': 'application/json',
        Authorization: tokenStore.token.type + ' ' + tokenStore.token.jwt
      }
    })
    if (response?.ok) {
      const response_json = await response.json()
      // success, modify state to online.
      console.log('RESTful online, got response: ', response_json)
      connStatusStore.connStatusState.restful = RestfulStatus.Online
      return response_json
    } else {
      // Got abnormal response code.
      console.log('Server reported an issue, HTTP Response Code: ', response?.status)
      connStatusStore.connStatusState.restful = RestfulStatus.Error
    }
  } catch (error) {
    if (error instanceof SyntaxError) {
      // Got abnormal data.
      console.log('Remoted returned non-json data.')
      connStatusStore.connStatusState.restful = RestfulStatus.Error
    } else if (error instanceof TypeError) {
      // Service down.
      console.log('Fetching remote resource failed, probably disconnected')
      connStatusStore.connStatusState.restful = RestfulStatus.Offline
    } else {
      // Other errors, probably user canceled request or network change.
      console.log('Unexpected error', error)
      connStatusStore.connStatusState.restful = RestfulStatus.Unknown
    }
  }
}
