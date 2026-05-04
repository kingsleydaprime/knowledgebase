# Validating .env in nodejs

## Using zod
```ts
import 'dotenv/config';
import dotenv from 'dotenv';
import { number, z } from 'zod';

dotenv.config();
const envSchema = z.object({
  PORT: z.string().default('5000'),
  NODE_ENV: z
    .enum(['development', 'production', 'staging'])
    .default('development'),
  MONGODB_URI: z.string().min(1, 'MONGODB_URI is required'),
  BASE_API_URL: z.string().default('http://localhost:3000/v1/api'),
  BASE_URL: z.string().min(1, 'BASE_URL is required'),
  CENOA_API_KEY: z.string().optional(),
  CENOA_API_SECRET: z.string().optional(),
  CENOA_ENVIRONMENT: z.enum(['sandbox', 'production']).default('sandbox'),

  TWILIO_AUTH_TOKEN: z.string().optional(),
  TWILIO_ACCOUNT_SID: z.string().optional(),
  SENDGRID_API_KEY: z.string().min(1, 'SENDGRID_API_KEY is required'),
  SENDGRID_SENDER_EMAIL: z
    .string()
    .email('SENDGRID_SENDER_EMAIL must be a valid email')
    .default('hello@mykaza.co'),
  CIRCLE_API_KEY: z.string().min(1, 'CIRCLE_API_KEY is required'),
  CIRCLE_APP_ID: z.string().optional(),
  CIRCLE_ENTITY_SECRET: z.string().min(1, 'CIRCLE_ENTITY_SECRET is required'),
  JWT_SECRET: z.string().min(1, 'JWT_SECRET is required'),
  TRANSAK_BASE_URL: z.string().optional(),
  TRANSAK_API_KEY: z.string().optional(),
  TRANSAK_API_SECRET: z.string().optional(),
  PRIVY_APP_ID: z.string().optional(),
  PRIVY_APP_SECRET: z.string().optional(),
  QUIDAX_RAMP_SECRET_KEY: z
    .string()
    .min(1, 'QUIDAX_RAMP_SECRET_KEY is required'),

  ONRAMPER_BASE_URL: z.string().optional(),
  ONRAMPER_API_KEY: z.string().optional(),
});

const parsedEnv = envSchema.safeParse(process.env);
if (!parsedEnv.success) {
  console.error(
    '❌ Invalid environment variables:',
    parsedEnv.error.flatten().fieldErrors
  );
  throw new Error('Invalid environment variables.');
}

export const env = parsedEnv.data;
```

## Extending using types in nodejs

`node.d.ts`
```ts
declare global {
  namespace NodeJS {
    interface ProcessEnv {
      NODE_ENV: 'development' | 'production' | 'test';
      PORT: string;
      JWT_SECRET: string;
      MONGODB_URI: string;
    }
  }
}

export { }
```