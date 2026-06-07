use dioxus::prelude::*;
use dioxus_router::Router;
use routes::router::Route;

mod api;
mod components;
mod routes;

fn main() {
    dioxus::launch(|| rsx! { Router::<Route> {} });
}
