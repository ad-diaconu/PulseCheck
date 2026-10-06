import { useState } from "react";

type CreateWorkspaceFormProps = {
  onCreate: (name: string) => Promise<void>;
};

const CreateWorkspaceForm = ({ onCreate }: CreateWorkspaceFormProps) => {
  const [name, setName] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setIsSubmitting(true);
    try {
      await onCreate(name.trim());
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-2">
      <input
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Workspace name"
        className="flex-1 px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900"
      />
      <button
        type="submit"
        disabled={isSubmitting || !name.trim()}
        className="px-3.5 py-2 text-sm font-medium rounded-lg bg-slate-900 text-white hover:bg-slate-800 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Create
      </button>
    </form>
  );
};

export default CreateWorkspaceForm;
