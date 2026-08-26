
const isDev = import.meta.env.MODE === 'development';

export const logger = {
    info: (msg: string, data?: any) => {
        if (isDev) console.log(`[INFO] ${msg}`, data || '');
    },
    error: (msg: string, error?: any) => {
        if (isDev) {
            console.error(`[ERROR] ${msg}`, error);
        } else {
            // Sentry: Sentry.captureException(error);
        }
    },
    warning: (msg: string, data?: any) => {
        if (isDev) console.warn(`[WARN] ${msg}`, data || '');
    }
};