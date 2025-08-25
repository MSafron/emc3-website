/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_APP_TITLE: string
  readonly DEV: boolean
  readonly PROD: boolean
  // Добавьте больше переменных окружения здесь...
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}