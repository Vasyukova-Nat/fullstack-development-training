export interface User {
    id: number;
    name: string;
    email: string;
}

export interface Task {
    id: number;
    title: string;
    description: string | null;
    user_id: number;
}

export interface UserWithTasks extends User {
    tasks: Task[];
}