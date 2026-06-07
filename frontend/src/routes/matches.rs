use crate::components::Matchcard;
use crate::components::Menu;
use dioxus::prelude::*;

#[component]
pub fn Matchesroute() -> Element {
    let profile_id = 1;
    rsx! {
        Menu {  }
        Matchcard {profile_id  }
    }
}
