# Error Handler in react

```ts
import axios, { AxiosError } from "axios";
import { ZodError } from "zod";

/**
 * Universal error handler
 * @param error - any unknown error
 * @returns human-readable string message
 */
export function errorHandler(error: unknown): string {
  try {
    // Axios error
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<any>;
      if (axiosError.response) {
        const data = axiosError.response.data;
        // Handle backend-defined error structures
        if (typeof data === "string") return data;
        if (data?.message) return data.message;
        if (data?.error) return data.error;
        return `Request failed with status ${axiosError.response.status}`;
      }
      if (axiosError.request) {
        return "No response received from the server. Please check your connection.";
      }
      return axiosError.message || "An unknown network error occurred.";
    }

    // Zod validation error
    if (error instanceof ZodError) {
      const firstError = error.errors?.[0];
      if (firstError?.message) return firstError.message;
      return "Validation failed. Please check your input data.";
    }

    // Fetch or network errors (non-Axios)
    if (error instanceof TypeError && error.message.includes("fetch")) {
      return "A network error occurred while fetching data.";
    }

    // Generic Error instance
    if (error instanceof Error) {
      if (error.message.includes("NetworkError")) return "Network error. Please try again.";
      if (error.message.includes("timeout")) return "Request timed out. Please retry.";
      return error.message || "An unexpected error occurred.";
    }

    // Custom error-like object
    if (typeof error === "object" && error !== null) {
      const errObj = error as Record<string, any>;
      if (errObj.message) return errObj.message;
      if (errObj.error) return errObj.error;
      if (errObj.detail) return errObj.detail;
    }

    // String errors
    if (typeof error === "string") return error;

    // Fallback
    return "Something went wrong. Please try again later.";
  } catch {
    // Safety net for unexpected internal failures
    return "Unexpected error occurred while handling another error.";
  }
}

```

> This will help handle errors and return an error message
