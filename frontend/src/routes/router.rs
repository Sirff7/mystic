use crate::routes::discover::Discoverroute;
use crate::routes::login::Loginroute;
use crate::routes::matches::Matchesroute;
use crate::routes::profile::Profileroute;

use dioxus::prelude::*;
use dioxus_router::Routable;

#[derive(Routable, Clone, PartialEq)]
pub enum Route {
    #[route("/")]
    Loginroute {},
    #[route("/discover")]
    Discoverroute {},
    #[route("/matches")]
    Matchesroute {},
    #[route("/profile")]
    Profileroute {},
}
