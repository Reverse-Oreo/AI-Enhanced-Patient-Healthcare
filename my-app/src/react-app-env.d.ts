/// <reference types="react-scripts" />

// Environment variables type declaration
declare namespace NodeJS {
  interface ProcessEnv {
    readonly REACT_APP_API_URL?: string;
    readonly REACT_APP_WS_URL?: string;
    readonly REACT_APP_URL?: string;
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