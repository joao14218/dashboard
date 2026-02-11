// --- AUTH SCRIPT ---
const currentUser = JSON.parse(sessionStorage.getItem('loggedInUser'));
const forceLogoutData = JSON.parse(localStorage.getItem('forceLogout'));

// 1. Definição das permissões
const permissions = {
    'CEO': ['dashboard.html', 'alunos.html', 'presenca.html', 'aulas.html', 'vendas.html', 'financas.html', 'usuarios.html', 'configuracoes.html'],
    'Administrador': ['dashboard.html', 'alunos.html', 'presenca.html', 'aulas.html', 'vendas.html', 'financas.html', 'usuarios.html', 'configuracoes.html'],
    'Professor': ['alunos.html', 'presenca.html', 'aulas.html'],
    'Vendedor': ['vendas.html']
};

if (!currentUser) {
    window.location.href = 'login.html';
} else if (forceLogoutData && currentUser.id !== forceLogoutData.adminId) {
    const lastLoginTime = currentUser.loginTimestamp || 0;
    if (forceLogoutData.timestamp > lastLoginTime) {
        sessionStorage.removeItem('loggedInUser');
        window.location.href = 'login.html';
    }
} else {
    const userPermissions = permissions[currentUser.role] || [];
    const currentPage = window.location.pathname.split('/').pop();
    if (userPermissions.length > 0 && !userPermissions.includes(currentPage)) {
        window.location.href = userPermissions[0];
    } else if (userPermissions.length === 0 && !userPermissions.includes(currentPage)) {
        sessionStorage.removeItem('loggedInUser');
        window.location.href = 'login.html';
    }
}

// 3. Estrutura do menu (Configurações adicionado no final)
const menuItems = [
    { name: 'Início', href: 'dashboard.html', icon: 'ph-house' },
    { name: 'Alunos', href: 'alunos.html', icon: 'ph-users' },
    { name: 'Presença', href: 'presenca.html', icon: 'ph-check-square' },
    { name: 'Aulas do Dia', href: 'aulas.html', icon: 'ph-chalkboard-teacher' },
    { name: 'Vendas', href: 'vendas.html', icon: 'ph-shopping-cart' },
    { name: 'Finanças', href: 'financas.html', icon: 'ph-currency-circle-dollar' },
    { name: 'Usuários', href: 'usuarios.html', icon: 'ph-user-gear' },
    { name: 'Configurações', href: 'configuracoes.html', icon: 'ph-gear' }
];

function generateSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (!sidebar || !currentUser) return;

    const userPermissions = permissions[currentUser.role] || [];
    const currentPage = window.location.pathname.split('/').pop();

    let menuHtml = `
        <div class="sidebar-header">
            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSNV8dxYF7dGp6TSUvr5KLLddCultBUPuo8XA&s" alt="Logo Arena Louzada">
            <h2>ARENA LOUZADA</h2>
            <p style="color: var(--text-muted); margin-top: 5px;">(${currentUser.role})</p>
        </div>
        <nav class="nav-menu">
    `;

    menuItems.forEach(item => {
        if (userPermissions.includes(item.href)) {
            const isActive = currentPage === item.href ? 'active' : '';
            menuHtml += `<a href="${item.href}" class="${isActive}"><i class="ph-fill ${item.icon}"></i> <span>${item.name}</span></a>`;
        }
    });
    
    menuHtml += `</nav><a href="#" id="logout-btn" style="text-decoration:none; color: var(--text-muted); text-align:center; padding:10px; font-weight:bold;">Sair</a>`;
    sidebar.innerHTML = menuHtml;
    
    document.getElementById('logout-btn').addEventListener('click', () => {
        sessionStorage.removeItem('loggedInUser');
        window.location.href = 'login.html';
    });
}

document.addEventListener('DOMContentLoaded', generateSidebar);
