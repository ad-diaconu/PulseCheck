import React from 'react'

type FormAlertProps = {
    type: 'error' | 'success',
    message: string | null,
}

const FormAlert = ({ type, message }: FormAlertProps) => {

    if (!message) return null;

    const isError = type === "error"
    const bgClass = isError ? 'bg-red-50 border-red-200 text-red-700' : 'bg-green-50 border-green-200 text-green-700';

    return (
        <div className={`mb-4 p-3 text-sm rounded-lg border ${bgClass}`}>
            {message}
        </div>
    )
}

export default FormAlert
