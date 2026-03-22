use log::info;

use fractyl_renderer::http::AxumRenderingServer;

#[tokio::main]
async fn main() { 
    colog::init();

    let server = AxumRenderingServer::new().discover_templates().unwrap();

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3001").await.unwrap();
    info!("Server running on http://localhost:3001");

    server.serve(listener).await.unwrap();
}
