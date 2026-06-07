use crate::components::sidebar::*;
use dioxus::prelude::*;

#[derive(Clone, PartialEq)]
struct NavMainItem {
    name: &'static str,
    url: &'static str,
}

const NAV_MAIN: &[NavMainItem] = &[
    NavMainItem {
        name: "Discover",
        url: "discover",
    },
    NavMainItem {
        name: "Matches",
        url: "matches",
    },
    NavMainItem {
        name: "Profile",
        url: "profile",
    },
];

#[component]
fn NavMain(items: &'static [NavMainItem]) -> Element {
    rsx! {
        SidebarGroup {
            SidebarMenu {
                for item in items.iter() {
                    SidebarMenuItem { key: "{item.name}",
                        SidebarMenuButton {
                            as: move |attributes: Vec<Attribute>| rsx! {
                                a { href: item.url, ..attributes,
                                    span { {item.name} }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

#[component]
pub fn Menu() -> Element {
    rsx! {
        SidebarProvider {
            Sidebar {
                side: SidebarSide::Left,
                variant: SidebarVariant::Sidebar,
                collapsible: SidebarCollapsible::Icon,
            }
            SidebarHeader {  }
            SidebarContent {
                NavMain { items: NAV_MAIN }
            }
            SidebarFooter {  }
            SidebarRail {  }
        }
    }
}
