const API_URL = 'http://localhost:8000/api';

export class RESTClient {
    private requestCount = 0;
    private totalSize = 0;
    private requests: { url: string; duration: number; size: number }[] = [];

    getStats() {
        return { count: this.requestCount, size: this.totalSize, requests: this.requests };
    }

    reset() {
        this.requestCount = 0;
        this.totalSize = 0;
        this.requests = [];
    }

    private async fetch(url: string, options?: RequestInit) {
        const start = Date.now();
        const res = await fetch(url, options);
        const data = await res.json();
        const size = JSON.stringify(data).length;
        
        this.requestCount++;
        this.totalSize += size;
        this.requests.push({ 
            url: url.split('/api')[1], 
            duration: Date.now() - start,
            size: size
        });
        
        return data;
    }

    async getUserWithTasks(userId: number) {
        const user = await this.fetch(`${API_URL}/users/${userId}`);
        const tasks = await this.fetch(`${API_URL}/tasks?user_id=${userId}`);
        return { ...user, tasks };
    }

    async getAllUsersWithTasks() {
        const users = await this.fetch(`${API_URL}/users`);
        const result = [];
        for (const user of users) {
            const tasks = await this.fetch(`${API_URL}/tasks?user_id=${user.id}`);
            result.push({ ...user, tasks });
        }
        return result;
    }

    async createUser(name: string, email: string) {
        return this.fetch(`${API_URL}/users`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email })
        });
    }

    async createTask(title: string, description: string, userId: number) {
        return this.fetch(`${API_URL}/tasks`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, description, user_id: userId })
        });
    }
}