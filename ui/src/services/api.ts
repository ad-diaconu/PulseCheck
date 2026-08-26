import axios from 'axios';
import { ApiError, AppError } from '../utils/errors';
import { logger } from "../utils/logger"

export const api = axios.create({
    baseURL: 'http://localhost:8000',
})

api.interceptors.response.use(
    (response) => response,
    (error) => {
        // network error
        if (!error.response) {
            logger.error('Network Error', error)
            throw new AppError("Can not connect to server")
        }

        const status = error.response.status;
        const detail = error.response.data?.detail || 'Unknown Server Error'
        logger.warning(`API Error ${status}: ${detail}`)

        // formatted error that can be used by any component
        throw new ApiError(detail, status)

    }
)