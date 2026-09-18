
const isDev = import.meta.env.MODE === 'development';

export const logger = {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any -- accepts any debug payload, like console.log
    info: (msg: string, data?: any) => {
        if (isDev) console.log(`[INFO] ${msg}`, data || '');
    },
    // eslint-disable-next-line @typescript-eslint/no-explicit-any -- accepts any debug payload, like console.log
    error: (msg: string, error?: any) => {
        if (isDev) {
            console.error(`[ERROR] ${msg}`, error);
        } else {
            // Sentry: Sentry.captureException(error);
        }
    },
    // eslint-disable-next-line @typescript-eslint/no-explicit-any -- accepts any debug payload, like console.log
    warning: (msg: string, data?: any) => {
        if (isDev) console.warn(`[WARN] ${msg}`, data || '');
    }
};