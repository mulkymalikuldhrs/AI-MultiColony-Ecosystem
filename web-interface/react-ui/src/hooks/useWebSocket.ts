import { useState, useEffect, useCallback, useRef } from 'react'

interface WebSocketMessage {
  type: string
  [key: string]: any
}

interface UseWebSocketOptions {
  onMessage?: (message: WebSocketMessage) => void
  onOpen?: () => void
  onClose?: () => void
  onError?: (error: Event) => void
  reconnectInterval?: number
  maxReconnectAttempts?: number
}

const useWebSocket = (url: string, options: UseWebSocketOptions = {}) => {
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const [reconnectAttempts, setReconnectAttempts] = useState(0)
  
  const websocketRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<number | null>(null)
  
  const {
    onMessage,
    onOpen,
    onClose,
    onError,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5
  } = options
  
  // Connect to WebSocket
  const connect = useCallback(() => {
    if (websocketRef.current?.readyState === WebSocket.OPEN) {
      return
    }
    
    websocketRef.current = new WebSocket(url)
    
    websocketRef.current.onopen = () => {
      setIsConnected(true)
      setReconnectAttempts(0)
      onOpen?.()
    }
    
    websocketRef.current.onclose = () => {
      setIsConnected(false)
      onClose?.()
      
      // Attempt to reconnect
      if (reconnectAttempts < maxReconnectAttempts) {
        reconnectTimeoutRef.current = window.setTimeout(() => {
          setReconnectAttempts(prev => prev + 1)
          connect()
        }, reconnectInterval)
      }
    }
    
    websocketRef.current.onerror = (error) => {
      onError?.(error)
    }
    
    websocketRef.current.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        setLastMessage(message)
        onMessage?.(message)
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }
  }, [url, onMessage, onOpen, onClose, onError, reconnectAttempts, maxReconnectAttempts, reconnectInterval])
  
  // Send message
  const sendMessage = useCallback((message: any) => {
    if (websocketRef.current?.readyState === WebSocket.OPEN) {
      websocketRef.current.send(JSON.stringify(message))
      return true
    }
    return false
  }, [])
  
  // Disconnect
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    
    if (websocketRef.current) {
      websocketRef.current.close()
      websocketRef.current = null
    }
  }, [])
  
  // Connect on mount, disconnect on unmount
  useEffect(() => {
    connect()
    
    return () => {
      disconnect()
    }
  }, [connect, disconnect])
  
  return {
    isConnected,
    lastMessage,
    sendMessage,
    connect,
    disconnect,
    reconnectAttempts
  }
}

export default useWebSocket