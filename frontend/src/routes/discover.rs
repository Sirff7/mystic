use crate::components::Menu;
use crate::components::Profilecard;
use dioxus::prelude::*;

#[component]
pub fn Discoverroute() -> Element {
    let liker_id = 42;
    rsx! {
        Menu {  }
        Profilecard {liker_id}
    }
}
