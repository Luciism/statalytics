use log::info;

use fractyl_renderer::http::AxumRenderingServer;
use fractyl_renderer::schema;

#[tokio::main]
async fn main() { 
    colog::init();

    let server = AxumRenderingServer::new().add_renderer(
        schema::load_schema_from_file("./exports/general-bedwars-stats/schema.json").unwrap(),
        "/bedwars",
    );

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3001").await.unwrap();
    info!("Server running on http://localhost:3001");

    server.serve(listener).await.unwrap();
}
