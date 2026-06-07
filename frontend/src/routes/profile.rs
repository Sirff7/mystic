use crate::components::Menu;
use crate::components::Profilecardform;
use dioxus::prelude::*;

#[component]
pub fn Profileroute() -> Element {
    let profile_id = 1;
    rsx! {
        Menu {  }
        Profilecardform { profile_id }
    }
}
