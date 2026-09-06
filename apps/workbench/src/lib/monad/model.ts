export type RepositorySource = {
  label: string;
  path: string;
  fileCount: number;
};

export type GitStatusEntry = {
  status: string;
  path: string;
};

export type RepositorySnapshot = {
  rootPath: string;
  branch: string;
  version: string | null;
  workbenchSpecificationPresent: boolean;
  sources: RepositorySource[];
  gitStatus: GitStatusEntry[];
};
