const GRAPHQL_URL = 'http://localhost:8000/graphql';

export class GraphQLClient {
    private requestCount = 0;
    private totalSize = 0;
    private requests: { duration: number; size: number }[] = [];

    getStats() {
        return { count: this.requestCount, size: this.totalSize, requests: this.requests };
    }

    reset() {
        this.requestCount = 0;
        this.totalSize = 0;
        this.requests = [];
    }

    private async query(query: string, vars?: any) {
        const start = Date.now();
        const res = await fetch(GRAPHQL_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, variables: vars })
        });
        const data = await res.json();
        const size = JSON.stringify(data).length;
        
        this.requestCount++;
        this.totalSize += size;
        this.requests.push({ duration: Date.now() - start, size: size });
        
        if (data.errors) throw new Error(data.errors[0].message);
        return data.data;
    }

    async getUserWithTasks(userId: number) {
        const data = await this.query(`
            query($id: Int!) {
                user(id: $id) {
                    id name email
                    tasks { id title description }
                }
            }
        `, { id: userId });
        return data?.user || null;
    }

    async getAllUsersWithTasks() {
        const data = await this.query(`
            {
                users {
                    id name email
                    tasks { id title description }
                }
            }
        `);
        return data?.users || [];
    }

    async createUser(name: string, email: string) {
        const data = await this.query(`
            mutation($input: CreateUserInput!) {
                createUser(input: $input) { id name email }
            }
        `, { input: { name, email } });
        return data?.createUser || null;
    }

    async createTask(title: string, description: string, userId: number) {
        const data = await this.query(`
            mutation($input: CreateTaskInput!) {
                createTask(input: $input) { id title description user_id }
            }
        `, { input: { title, description, user_id: userId } });
        return data?.createTask || null;
    }
}