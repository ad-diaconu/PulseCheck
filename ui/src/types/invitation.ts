export type InvitationStatus = "pending" | "accepted" | "declined";

export type Invitation = {
  id: string;
  workspace_id: string;
  invited_user_id: string;
  invited_by_user_id: string;
  role: string;
  status: InvitationStatus;
  created_at: string;
  responded_at: string | null;
};

export type InvitationWithEmail = Invitation & {
  invited_email: string;
};

export type InvitationWithContext = Invitation & {
  workspace_name: string;
  invited_by_email: string;
};
