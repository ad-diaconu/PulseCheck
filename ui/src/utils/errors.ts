export class AppError extends Error {
    constructor(public message: string, public code?: string) {
        super(message)
        this.name = "AppError";
    }
}

export class ApiError extends AppError {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any -- backend error payload shape varies
    constructor(message: string, public status: number, public data?: any) {
        super(message, 'API_ERROR')
        this.name = 'ApiError';
    }
}