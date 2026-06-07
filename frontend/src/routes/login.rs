use crate::components::Logincard;
use dioxus::prelude::*;

#[component]
pub fn Loginroute() -> Element {
    rsx! {
        Logincard {}
    }
}
