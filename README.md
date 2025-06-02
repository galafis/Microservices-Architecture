# Microservices Architecture

[English](#english) | [Português](#português)

## English

### Overview
Modern microservices architecture implementation with Python and Flask. Demonstrates distributed system design patterns, service communication, API gateway, service discovery, and containerization. Built for scalability, maintainability, and fault tolerance.

### Features
- **Service-Oriented Architecture**: Modular, independent services
- **API Gateway**: Centralized request routing and management
- **Service Discovery**: Automatic service registration and discovery
- **Load Balancing**: Distributed request handling
- **Health Monitoring**: Service health checks and monitoring
- **Configuration Management**: Centralized configuration service
- **Inter-Service Communication**: REST APIs and message queues
- **Containerization**: Docker support for deployment

### Technologies Used
- **Python 3.8+**
- **Flask**: Microservice framework
- **Docker**: Containerization platform
- **Redis**: Caching and message broker
- **SQLite**: Individual service databases
- **Nginx**: Load balancer and reverse proxy
- **JSON**: Service communication format

### Installation

1. Clone the repository:
```bash
git clone https://github.com/galafis/Microservices-Architecture.git
cd Microservices-Architecture
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the services:
```bash
# Start API Gateway
python app.py

# Start individual services (in separate terminals)
python services/user_service.py
python services/product_service.py
python services/order_service.py
```

4. Open your browser to `http://localhost:5000`

### Architecture Overview

#### Core Services
- **API Gateway**: Request routing and authentication
- **User Service**: User management and authentication
- **Product Service**: Product catalog and inventory
- **Order Service**: Order processing and management
- **Notification Service**: Email and SMS notifications

#### Infrastructure Services
- **Service Registry**: Service discovery and health monitoring
- **Configuration Service**: Centralized configuration management
- **Logging Service**: Centralized logging and monitoring
- **Cache Service**: Redis-based caching layer

### Service Communication

#### REST APIs
```python
# User Service API
GET /api/users/{user_id}
POST /api/users
PUT /api/users/{user_id}
DELETE /api/users/{user_id}

# Product Service API
GET /api/products
GET /api/products/{product_id}
POST /api/products
PUT /api/products/{product_id}

# Order Service API
GET /api/orders
POST /api/orders
GET /api/orders/{order_id}
PUT /api/orders/{order_id}/status
```

#### Message Queues
```python
# Asynchronous communication
from services.messaging import MessageQueue

queue = MessageQueue()

# Publish order event
queue.publish('order.created', {
    'order_id': 123,
    'user_id': 456,
    'total': 99.99
})

# Subscribe to events
@queue.subscribe('order.created')
def handle_order_created(data):
    send_confirmation_email(data['user_id'])
```

### API Gateway

#### Request Routing
```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Service registry
SERVICES = {
    'users': 'http://localhost:5001',
    'products': 'http://localhost:5002',
    'orders': 'http://localhost:5003'
}

@app.route('/api/<service>/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_request(service, endpoint):
    if service not in SERVICES:
        return jsonify({'error': 'Service not found'}), 404
    
    service_url = f"{SERVICES[service]}/api/{endpoint}"
    response = requests.request(
        method=request.method,
        url=service_url,
        json=request.get_json(),
        params=request.args
    )
    
    return jsonify(response.json()), response.status_code
```

#### Authentication & Authorization
```python
from functools import wraps
import jwt

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user = payload
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated_function
```

### Service Discovery

#### Service Registration
```python
import requests
import threading
import time

class ServiceRegistry:
    def __init__(self, registry_url):
        self.registry_url = registry_url
        self.services = {}
    
    def register_service(self, name, url, health_check_url):
        service_data = {
            'name': name,
            'url': url,
            'health_check': health_check_url,
            'timestamp': time.time()
        }
        
        response = requests.post(
            f"{self.registry_url}/register",
            json=service_data
        )
        
        if response.status_code == 200:
            # Start health check thread
            threading.Thread(
                target=self._health_check_loop,
                args=(name, health_check_url),
                daemon=True
            ).start()
    
    def _health_check_loop(self, name, health_url):
        while True:
            try:
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    self._update_service_status(name, 'healthy')
                else:
                    self._update_service_status(name, 'unhealthy')
            except:
                self._update_service_status(name, 'unhealthy')
            
            time.sleep(30)  # Check every 30 seconds
```

### Load Balancing

#### Round Robin Load Balancer
```python
import itertools

class LoadBalancer:
    def __init__(self):
        self.services = {}
    
    def add_service_instances(self, service_name, instances):
        self.services[service_name] = itertools.cycle(instances)
    
    def get_service_instance(self, service_name):
        if service_name in self.services:
            return next(self.services[service_name])
        return None

# Usage
lb = LoadBalancer()
lb.add_service_instances('user-service', [
    'http://user-service-1:5001',
    'http://user-service-2:5001',
    'http://user-service-3:5001'
])

# Get next available instance
instance = lb.get_service_instance('user-service')
```

### Configuration Management

#### Centralized Configuration
```python
import os
import json
import requests

class ConfigService:
    def __init__(self, config_service_url):
        self.config_url = config_service_url
        self.cache = {}
    
    def get_config(self, service_name, key=None):
        cache_key = f"{service_name}:{key}" if key else service_name
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        url = f"{self.config_url}/config/{service_name}"
        if key:
            url += f"/{key}"
        
        response = requests.get(url)
        if response.status_code == 200:
            config = response.json()
            self.cache[cache_key] = config
            return config
        
        return None

# Usage
config = ConfigService('http://config-service:5010')
db_config = config.get_config('user-service', 'database')
```

### Monitoring & Logging

#### Health Checks
```python
from flask import Flask, jsonify
import psutil
import time

app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'user-service',
        'version': '1.0.0',
        'uptime': time.time() - start_time,
        'memory_usage': psutil.virtual_memory().percent,
        'cpu_usage': psutil.cpu_percent()
    })

@app.route('/metrics')
def metrics():
    return jsonify({
        'requests_total': request_counter,
        'requests_per_second': calculate_rps(),
        'average_response_time': calculate_avg_response_time(),
        'error_rate': calculate_error_rate()
    })
```

#### Distributed Logging
```python
import logging
import json
from datetime import datetime

class MicroserviceLogger:
    def __init__(self, service_name, log_service_url):
        self.service_name = service_name
        self.log_service_url = log_service_url
        
        # Configure local logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(service_name)
    
    def log(self, level, message, **kwargs):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'service': self.service_name,
            'level': level,
            'message': message,
            'metadata': kwargs
        }
        
        # Log locally
        self.logger.log(getattr(logging, level.upper()), message)
        
        # Send to centralized logging service
        try:
            requests.post(
                f"{self.log_service_url}/logs",
                json=log_entry,
                timeout=1
            )
        except:
            pass  # Don't fail if logging service is down
```

### Docker Configuration

#### Dockerfile Example
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  api-gateway:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SERVICE_NAME=api-gateway
    depends_on:
      - redis
      - user-service
      - product-service

  user-service:
    build: ./services/user-service
    ports:
      - "5001:5001"
    environment:
      - SERVICE_NAME=user-service
      - DATABASE_URL=sqlite:///users.db

  product-service:
    build: ./services/product-service
    ports:
      - "5002:5002"
    environment:
      - SERVICE_NAME=product-service

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

### Security

#### Service-to-Service Authentication
```python
import jwt
import time

class ServiceAuth:
    def __init__(self, secret_key):
        self.secret_key = secret_key
    
    def generate_service_token(self, service_name):
        payload = {
            'service': service_name,
            'iat': time.time(),
            'exp': time.time() + 3600  # 1 hour
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_service_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload['service']
        except jwt.InvalidTokenError:
            return None
```

### Testing

#### Integration Testing
```python
import unittest
import requests

class MicroservicesIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.api_gateway_url = 'http://localhost:5000'
    
    def test_user_creation_flow(self):
        # Create user
        user_data = {'name': 'John Doe', 'email': 'john@example.com'}
        response = requests.post(f"{self.api_gateway_url}/api/users", json=user_data)
        self.assertEqual(response.status_code, 201)
        
        user_id = response.json()['id']
        
        # Verify user exists
        response = requests.get(f"{self.api_gateway_url}/api/users/{user_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['email'], 'john@example.com')
```

### Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Português

### Visão Geral
Implementação moderna de arquitetura de microserviços com Python e Flask. Demonstra padrões de design de sistemas distribuídos, comunicação entre serviços, gateway de API, descoberta de serviços e containerização. Construído para escalabilidade, manutenibilidade e tolerância a falhas.

### Funcionalidades
- **Arquitetura Orientada a Serviços**: Serviços modulares e independentes
- **Gateway de API**: Roteamento centralizado e gerenciamento de requisições
- **Descoberta de Serviços**: Registro e descoberta automática de serviços
- **Balanceamento de Carga**: Tratamento distribuído de requisições
- **Monitoramento de Saúde**: Verificações de saúde e monitoramento de serviços
- **Gerenciamento de Configuração**: Serviço de configuração centralizado
- **Comunicação Inter-Serviços**: APIs REST e filas de mensagens
- **Containerização**: Suporte Docker para deployment

### Tecnologias Utilizadas
- **Python 3.8+**
- **Flask**: Framework de microserviços
- **Docker**: Plataforma de containerização
- **Redis**: Cache e message broker
- **SQLite**: Bancos de dados de serviços individuais
- **Nginx**: Load balancer e reverse proxy
- **JSON**: Formato de comunicação entre serviços

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/galafis/Microservices-Architecture.git
cd Microservices-Architecture
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute os serviços:
```bash
# Iniciar API Gateway
python app.py

# Iniciar serviços individuais (em terminais separados)
python services/user_service.py
python services/product_service.py
python services/order_service.py
```

4. Abra seu navegador em `http://localhost:5000`

### Visão Geral da Arquitetura

#### Serviços Principais
- **Gateway de API**: Roteamento de requisições e autenticação
- **Serviço de Usuário**: Gerenciamento de usuários e autenticação
- **Serviço de Produto**: Catálogo de produtos e inventário
- **Serviço de Pedido**: Processamento e gerenciamento de pedidos
- **Serviço de Notificação**: Notificações por email e SMS

#### Serviços de Infraestrutura
- **Registro de Serviços**: Descoberta de serviços e monitoramento de saúde
- **Serviço de Configuração**: Gerenciamento centralizado de configuração
- **Serviço de Logging**: Logging e monitoramento centralizados
- **Serviço de Cache**: Camada de cache baseada em Redis

### Comunicação entre Serviços

#### APIs REST
```python
# API do Serviço de Usuário
GET /api/users/{user_id}
POST /api/users
PUT /api/users/{user_id}
DELETE /api/users/{user_id}

# API do Serviço de Produto
GET /api/products
GET /api/products/{product_id}
POST /api/products
PUT /api/products/{product_id}

# API do Serviço de Pedido
GET /api/orders
POST /api/orders
GET /api/orders/{order_id}
PUT /api/orders/{order_id}/status
```

#### Filas de Mensagens
```python
# Comunicação assíncrona
from services.messaging import MessageQueue

queue = MessageQueue()

# Publicar evento de pedido
queue.publish('order.created', {
    'order_id': 123,
    'user_id': 456,
    'total': 99.99
})

# Subscrever a eventos
@queue.subscribe('order.created')
def handle_order_created(data):
    send_confirmation_email(data['user_id'])
```

### Gateway de API

#### Roteamento de Requisições
```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Registro de serviços
SERVICES = {
    'users': 'http://localhost:5001',
    'products': 'http://localhost:5002',
    'orders': 'http://localhost:5003'
}

@app.route('/api/<service>/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_request(service, endpoint):
    if service not in SERVICES:
        return jsonify({'error': 'Serviço não encontrado'}), 404
    
    service_url = f"{SERVICES[service]}/api/{endpoint}"
    response = requests.request(
        method=request.method,
        url=service_url,
        json=request.get_json(),
        params=request.args
    )
    
    return jsonify(response.json()), response.status_code
```

### Contribuindo
1. Faça um fork do repositório
2. Crie uma branch de feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adicionar nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

### Licença
Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

