/// <reference types="react-scripts" />

// Environment variables type declaration
declare namespace NodeJS {
  interface ProcessEnv {
    readonly REACT_APP_SUPABASE_URL?: string;
    readonly REACT_APP_SUPABASE_ANON_KEY?: string;
    readonly REACT_APP_API_URL?: string;
    readonly REACT_APP_WS_URL?: string;
    readonly REACT_APP_URL?: string;
    readonly REACT_APP_BYPASS_AUTH?: string;
    readonly REACT_APP_SHOW_DEMO_WHEN_LOGGED_OUT?: string;
    readonly REACT_APP_INCLUDE_DEMO_WHEN_LOGGED_IN?: string;
  }
}

// Global process declaration for React apps
declare const process: {
  env: NodeJS.ProcessEnv;
};

// Tells TypeScript that .svg files can be imported as strings
declare module "*.svg" {
  const content: string;
  export default content;
}

declare module "*.png" {
  const content: string;
  export default content;
}

declare module "*.jpg" {
  const content: string;
  export default content;
}