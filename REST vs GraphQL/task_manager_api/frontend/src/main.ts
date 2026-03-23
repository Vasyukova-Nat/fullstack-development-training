import { RESTClient } from './rest-client';
import { GraphQLClient } from './graphql-client';

const rest = new RESTClient();
const graphql = new GraphQLClient();

// DOM элементы
const restSelect = document.getElementById('rest-user-select') as HTMLSelectElement;
const graphqlSelect = document.getElementById('graphql-user-select') as HTMLSelectElement;
const restResult = document.getElementById('rest-result') as HTMLDivElement;
const graphqlResult = document.getElementById('graphql-result') as HTMLDivElement;
const restStatsDiv = document.getElementById('rest-stats') as HTMLDivElement;
const graphqlStatsDiv = document.getElementById('graphql-stats') as HTMLDivElement;

function updateStats() {
    const restStats = rest.getStats();
    const graphqlStats = graphql.getStats();
    restStatsDiv.innerHTML = `Запросов: ${restStats.count} | Данных: ${(restStats.size / 1024).toFixed(1)} KB`;
    graphqlStatsDiv.innerHTML = `Запросов: ${graphqlStats.count} | Данных: ${(graphqlStats.size / 1024).toFixed(1)} KB`;
}

function showResult(container: HTMLDivElement, title: string, data: any, requests: any[], totalSize: number, isGraphQL = false) {
    container.classList.remove('hidden');
    const badge = isGraphQL ? 'badge-graphql' : 'badge-rest';
    container.innerHTML = `
        <div class="result-header">
            <div class="result-title">${title}</div>
            <div class="result-stats">
                <span class="${badge}">Запросов: ${requests.length}</span>
                <span class="${badge}">Данных: ${(totalSize / 1024).toFixed(1)} KB</span>
            </div>
        </div>
        <div class="result-info">
            <strong>Запросы:</strong>
            <ul>
                ${requests.map(r => `<li>${r.url || 'POST /graphql'} (${r.duration}ms, ${(r.size / 1024).toFixed(1)} KB)</li>`).join('')}
            </ul>
            ${!isGraphQL && requests.length > 1 ? '<p class="highlight">Потребовалось 2 запроса вместо 1</p>' : ''}
            ${isGraphQL && requests.length === 1 ? '<p class="highlight">Все данные за 1 запрос</p>' : ''}
        </div>
        <pre>${JSON.stringify(data, null, 2)}</pre>
    `;
}

// REST: выбор пользователя
restSelect.onchange = async () => {
    const id = parseInt(restSelect.value);
    if (!id) return restResult.classList.add('hidden');
    
    restResult.classList.remove('hidden');
    restResult.innerHTML = '<div class="loading">Загрузка...</div>';
    
    const user = await rest.getUserWithTasks(id);
    const stats = rest.getStats();
    const lastRequests = stats.requests.slice(-2);
    const lastSize = lastRequests.reduce((sum, r) => sum + r.size, 0);
    
    showResult(restResult, `Пользователь ${user.name}`, user, lastRequests, lastSize);
    updateStats();
};

// GraphQL: выбор пользователя
graphqlSelect.onchange = async () => {
    const id = parseInt(graphqlSelect.value);
    if (!id) return graphqlResult.classList.add('hidden');
    
    graphqlResult.classList.remove('hidden');
    graphqlResult.innerHTML = '<div class="loading">Загрузка...</div>';
    
    const user = await graphql.getUserWithTasks(id);
    const stats = graphql.getStats();
    const lastRequest = stats.requests[stats.requests.length - 1];
    
    showResult(graphqlResult, `Пользователь ${user?.name}`, user, [lastRequest], lastRequest?.size || 0, true);
    updateStats();
};

// REST: все пользователи
document.getElementById('rest-all-users')!.onclick = async () => {
    restResult.classList.remove('hidden');
    restResult.innerHTML = '<div class="loading">Загрузка...</div>';
    
    const users = await rest.getAllUsersWithTasks();
    const stats = rest.getStats();
    
    restResult.innerHTML = `
        <div class="result-header">
            <div class="result-title">Получено ${users.length} пользователей</div>
            <div class="result-stats">
                <span class="badge-rest">Запросов: ${stats.count}</span>
                <span class="badge-rest">Данных: ${(stats.size / 1024).toFixed(1)} KB</span>
            </div>
        </div>
        <div class="result-info">
            <strong>Проблема REST:</strong> нужно N+1 запросов: 1 запрос на список пользователей + ${users.length} запросов на задачи. 
        </div>
        <pre>${JSON.stringify(users, null, 2)}</pre>
    `;
    updateStats();
};

// GraphQL: все пользователи
document.getElementById('graphql-all-users')!.onclick = async () => {
    graphqlResult.classList.remove('hidden');
    graphqlResult.innerHTML = '<div class="loading">Загрузка...</div>';
    
    const users = await graphql.getAllUsersWithTasks();
    const stats = graphql.getStats();
    
    graphqlResult.innerHTML = `
        <div class="result-header">
            <div class="result-title">Получено ${users.length} пользователей</div>
            <div class="result-stats">
                <span class="badge-graphql">Запросов: ${stats.count}</span>
                <span class="badge-graphql">Данных: ${(stats.size / 1024).toFixed(1)} KB</span>
            </div>
        </div>
        <div class="result-info">
            <strong>Преимущество GraphQL:</strong> все данные за <strong>1 запрос</strong> независимо от количества пользователей    
        </div>
        <pre>${JSON.stringify(users, null, 2)}</pre>
    `;
    updateStats();
};

// Показать детальную статистику
document.getElementById('rest-metrics')!.onclick = () => {
    const stats = rest.getStats();
    alert(`REST API\nВсего запросов: ${stats.count}\nОбъем данных: ${(stats.size / 1024).toFixed(1)} KB\n\nДетали:\n${stats.requests.map((r, i) => `${i+1}. ${r.url} (${r.duration}ms, ${(r.size / 1024).toFixed(1)} KB)`).join('\n')}`);
};

document.getElementById('graphql-metrics')!.onclick = () => {
    const stats = graphql.getStats();
    alert(`GraphQL API\nВсего запросов: ${stats.count}\nОбъем данных: ${(stats.size / 1024).toFixed(1)} KB\n\nСреднее время: ${(stats.requests.reduce((s, r) => s + r.duration, 0) / stats.count || 0).toFixed(0)}ms`);
};

// Сброс метрик
document.getElementById('reset-metrics')!.onclick = () => {
    rest.reset();
    graphql.reset();
    updateStats();
    restResult.classList.add('hidden');
    graphqlResult.classList.add('hidden');
};

// Создание пользователя
document.getElementById('create-user-form')!.onsubmit = async (e) => {
    e.preventDefault();
    const name = (document.getElementById('user-name') as HTMLInputElement).value;
    const email = (document.getElementById('user-email') as HTMLInputElement).value;
    
    if (!name || !email) return alert('Заполните все поля');
    
    await rest.createUser(name, email);
    await graphql.createUser(name, email);
    
    alert(`Пользователь "${name}" создан`);
    (e.target as HTMLFormElement).reset();
    
    // Обновляем списки
    const restUsers = await rest.getAllUsersWithTasks();
    const graphqlUsers = await graphql.getAllUsersWithTasks();
    restSelect.innerHTML = '<option value="">Выберите пользователя</option>' + restUsers.map((u: any) => `<option value="${u.id}">${u.name} (${u.tasks.length} задач)</option>`).join('');
    graphqlSelect.innerHTML = '<option value="">Выберите пользователя</option>' + graphqlUsers.map((u: any) => `<option value="${u.id}">${u.name} (${u.tasks.length} задач)</option>`).join('');
    updateStats();
};

// Создание задачи
document.getElementById('create-task-form')!.onsubmit = async (e) => {
    e.preventDefault();
    const title = (document.getElementById('task-title') as HTMLInputElement).value;
    const desc = (document.getElementById('task-description') as HTMLTextAreaElement).value;
    const userId = parseInt((document.getElementById('task-user-id') as HTMLInputElement).value);
    
    if (!title || !userId) return alert('Заполните заголовок и ID пользователя');
    
    await rest.createTask(title, desc, userId);
    await graphql.createTask(title, desc, userId);
    
    alert(`Задача "${title}" создана`);
    (e.target as HTMLFormElement).reset();
    updateStats();
};

// Инициализация
(async () => {
    const restUsers = await rest.getAllUsersWithTasks();
    const graphqlUsers = await graphql.getAllUsersWithTasks();
    restSelect.innerHTML = '<option value="">Выберите пользователя</option>' + restUsers.map((u: any) => `<option value="${u.id}">${u.name} (${u.tasks.length} задач)</option>`).join('');
    graphqlSelect.innerHTML = '<option value="">Выберите пользователя</option>' + graphqlUsers.map((u: any) => `<option value="${u.id}">${u.name} (${u.tasks.length} задач)</option>`).join('');
    restResult.classList.add('hidden');
    graphqlResult.classList.add('hidden');
})();