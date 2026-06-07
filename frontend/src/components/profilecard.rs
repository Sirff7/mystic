use crate::api::models::CouplesRequest;
use crate::api::models::DiscoveryRequest;
use crate::api::models::DiscoveryResponse;
use crate::api::models::LikeRequest;
use crate::api::models::MatchResponse;
use crate::api::models::UpdateProfileRequest;
use crate::components::button::{Button, ButtonVariant};
use crate::components::card::*;
use crate::components::input::Input;
use crate::components::label::Label;
use crate::components::tabs::*;
use dioxus::prelude::*;

// Discovery
async fn discover() -> Result<DiscoveryResponse, reqwest::Error> {
    let profile = reqwest::Client::new()
        .post(format!("http://localhost:8000/discoveries"))
        .json(&DiscoveryRequest { profile_id: 1 })
        .send()
        .await?
        .error_for_status()?
        .json::<DiscoveryResponse>()
        .await?;

    Ok(profile)
}

async fn like(liker_id: i32, liked_id: i32, status: i32) -> Result<(), reqwest::Error> {
    reqwest::Client::new()
        .post("http://localhost:8000/likes")
        .json(&LikeRequest {
            liker_id,
            liked_id,
            status,
        })
        .send()
        .await?
        .error_for_status()?;

    Ok(())
}

#[component]
pub fn Profilecard(liker_id: i32) -> Element {
    let mut profile = use_signal(|| None::<DiscoveryResponse>);
    let mut error = use_signal(|| None::<String>);

    use_effect(move || {
        spawn(async move {
            match discover().await {
                Ok(next_profile) => profile.set(Some(next_profile)),
                Err(err) => error.set(Some(format!("Initial Discovery failed: {err}"))),
            }
        });
    });
    let like_current = move |_| async move {
        if let Some(p) = profile() {
            match like(liker_id, p.profile_id, 1).await {
                Ok(_) => match discover().await {
                    Ok(next_profile) => profile.set(Some(next_profile)),
                    Err(err) => error.set(Some(format!("Discovery failed: {err}"))),
                },
                Err(err) => error.set(Some(format!("Like failed: {err}"))),
            }
        }
    };
    let skip_current = move |_| async move {
        if let Some(p) = profile() {
            match like(liker_id, p.profile_id, 0).await {
                Ok(_) => match discover().await {
                    Ok(next_profile) => profile.set(Some(next_profile)),
                    Err(err) => error.set(Some(format!("Discovery failed: {err}"))),
                },
                Err(err) => error.set(Some(format!("Skip failed: {err}"))),
            }
        }
    };
    rsx! {
        Card { style: "width: 100%; max-width: 24rem;",
            CardHeader {
                CardTitle { "Profile" }
            }
            CardContent {
                match profile() {
                    Some(p) => rsx! {
                        div { style: "display: flex; flex-direction: column; gap: 1.5rem;",
                            div { style: "display: grid; gap: 0.5rem;",
                                Profiletabs {
                                    display_name: p.display_name.clone(),
                                    bio: p.bio.clone(),
                                    zodiac: p.zodiac.clone(),
                                }
                            }
                        }
                    },
                    None => rsx! {
                        p { "No profile loaded yet." }
                    }
                }
            }
            CardFooter { style: "flex-direction: column; gap: 0.5rem;",
                Button {
                    variant: ButtonVariant::Primary,
                    style: "width: 100%;",
                    onclick: like_current,
                    "Like"
                }
                Button {
                    variant: ButtonVariant::Outline,
                    style: "width: 100%;",
                    onclick: skip_current,
                    "Skip"
                }
            }
            if let Some(message) = error() {
                p {style: "color: red; font-size: o.875rem;", "{message}" }
            }
        }
    }
}

#[component]
fn Profiletabs(display_name: String, bio: String, zodiac: String) -> Element {
    rsx! {
        Tabs {
            default_value: "tab1".to_string(),
            horizontal: true,
            max_width: "16rem",
            TabList {
                TabTrigger { value: "tab1".to_string(), index: 0usize, "Name" }
                TabTrigger { value: "tab2".to_string(), index: 1usize, "Zodiac" }
                TabTrigger { value: "tab3".to_string(), index: 2usize, "Bio" }
            }
            TabContent { index: 0usize, value: "tab1".to_string(),
                div {
                    width: "100%",
                    height: "5rem",
                    display: "flex",
                    align_items: "center",
                    justify_content: "center",
                    "{display_name}"
                }
            }
            TabContent {
                index: 1usize,
                value: "tab2".to_string(),
                div {
                    width: "100%",
                    height: "5rem",
                    display: "flex",
                    align_items: "center",
                    justify_content: "center",
                    "{zodiac}"
                }
            }
            TabContent { index: 2usize, value: "tab3".to_string(),
                div {
                    width: "100%",
                    height: "5rem",
                    display: "flex",
                    align_items: "center",
                    justify_content: "center",
                    "{bio}"
                }
            }
        }
    }
}
// Profile updating
async fn update_profile(
    profile_id: i32,
    display_name: String,
    bio: String,
    zodiac: String,
) -> Result<(), reqwest::Error> {
    reqwest::Client::new()
        .put("http://localhost:8000/profiles")
        .json(&UpdateProfileRequest {
            profile_id,
            display_name,
            bio,
            zodiac,
        })
        .send()
        .await?
        .error_for_status()?;

    Ok(())
}

#[component]
pub fn Profilecardform(profile_id: i32) -> Element {
    rsx! {
        Card { style: "width: 100%; max-width: 24rem;",
            CardHeader {
                CardTitle { "Your Profile" }
            }
            CardContent {
                div { style: "display: flex; flex-direction: column; gap: 1.5rem;",
                    div { style: "display: grid; gap: 0.5rem;",
                        Profiletabsform { profile_id }
                    }
                }
            }
        }
    }
}

#[component]
fn Profiletabsform(profile_id: i32) -> Element {
    let mut bio = use_signal(String::new);
    let mut display_name = use_signal(String::new);
    let mut zodiac = use_signal(String::new);

    let mut success = use_signal(|| None::<String>);
    let mut error = use_signal(|| None::<String>);
    let mut loading = use_signal(|| false);

    rsx! {
        form {
            id: "update-form",

            onsubmit: move |event| async move {
                event.prevent_default();

                loading.set(true);
                success.set(None);
                error.set(None);

                let result = update_profile(
                    profile_id,
                    display_name(),
                    bio(),
                    zodiac(),
                ).await;

                loading.set(false);

                match result {
                    Ok(_) => {
                        success.set(Some("Profile updated".to_string()));
                    }
                    Err(err) => {
                        error.set(Some(format!("Profile update failed: {err}")));
                    }
                }
            },

            Tabs {
                default_value: "tab1".to_string(),
                horizontal: true,
                max_width: "16rem",

                TabList {
                    TabTrigger {
                        value: "tab1".to_string(),
                        index: 0usize,
                        "Name"
                    }
                    TabTrigger {
                        value: "tab2".to_string(),
                        index: 1usize,
                        "Zodiac"
                    }
                    TabTrigger {
                        value: "tab3".to_string(),
                        index: 2usize,
                        "Bio"
                    }
                }

                TabContent {
                    index: 0usize,
                    value: "tab1".to_string(),

                    div { style: "display: grid; gap: 0.5rem;",
                        Label {
                            html_for: "display_name",
                            "New name:"
                        }

                        Input {
                            id: "display_name",
                            name: "display_name",
                            r#type: "text",
                            placeholder: "Write your name",
                            value: display_name(),
                            oninput: move |event: Event<FormData>| {
                                display_name.set(event.value());
                            }
                        }
                    }
                }

                TabContent {
                    index: 1usize,
                    value: "tab2".to_string(),

                    div { style: "display: grid; gap: 0.5rem;",
                        Label {
                            html_for: "zodiac",
                            "New zodiac:"
                        }

                        Input {
                            id: "zodiac",
                            name: "zodiac",
                            r#type: "text",
                            placeholder: "Write your zodiac sign",
                            value: zodiac(),
                            oninput: move |event: Event<FormData>| {
                                zodiac.set(event.value());
                            }
                        }
                    }
                }

                TabContent {
                    index: 2usize,
                    value: "tab3".to_string(),

                    div { style: "display: grid; gap: 0.5rem;",
                        Label {
                            html_for: "bio",
                            "New bio:"
                        }

                        Input {
                            id: "bio",
                            name: "bio",
                            r#type: "text",
                            placeholder: "Write something about yourself",
                            value: bio(),
                            oninput: move |event: Event<FormData>| {
                                bio.set(event.value());
                            }
                        }
                    }
                }
            }

            Button {
                variant: ButtonVariant::Primary,
                r#type: "submit",
                style: "width: 100%; margin-top: 1rem;",
                if loading() {
                    "Updating..."
                } else {
                    "Update"
                }
            }

            if let Some(message) = success() {
                p {
                    style: "color: green; font-size: 0.875rem;",
                    "{message}"
                }
            }

            if let Some(message) = error() {
                p {
                    style: "color: red; font-size: 0.875rem;",
                    "{message}"
                }
            }
        }
    }
}

// Matches
async fn get_matches(profile_id: i32, index: i32) -> Result<MatchResponse, reqwest::Error> {
    let matched_profile = reqwest::Client::new()
        .post("http://localhost:8000/couples")
        .json(&CouplesRequest { profile_id, index })
        .send()
        .await?
        .error_for_status()?
        .json::<MatchResponse>()
        .await?;

    Ok(matched_profile)
}

#[component]
pub fn Matchcard(profile_id: i32) -> Element {
    rsx! {
        Card { style: "width: 100%; max-width: 24rem;",
            CardHeader {
                CardTitle { "Match" }
            }
            CardContent {
                div { style: "display: flex; flex-direction: column; gap: 1.5rem;",
                    div { style: "display: grid; gap: 0.5rem;",
                        Matchtabs { profile_id }
                    }
                }
            }
        }
    }
}
#[component]
fn Matchtabs(profile_id: i32) -> Element {
    let mut index = use_signal(|| 0);
    let mut current_match = use_signal(|| None::<MatchResponse>);
    let mut error = use_signal(|| None::<String>);
    let mut loading = use_signal(|| false);

    use_effect(move || {
        spawn(async move {
            loading.set(true);
            error.set(None);

            let result = get_matches(profile_id, index()).await;

            loading.set(false);

            match result {
                Ok(profile) => {
                    current_match.set(Some(profile));
                }
                Err(err) => {
                    error.set(Some(format!("Could not load match: {err}")));
                }
            }
        });
    });
    rsx! {
        div {
            Tabs {
                default_value: "tab1".to_string(),
                horizontal: true,
                max_width: "16rem",

                TabList {
                    TabTrigger { value: "tab1".to_string(), index: 0usize, "Name" }
                    TabTrigger { value: "tab2".to_string(), index: 1usize, "Zodiac" }
                    TabTrigger { value: "tab3".to_string(), index: 2usize, "Bio" }
                }

                TabContent { index: 0usize, value: "tab1".to_string(),
                    div {
                        width: "100%",
                        height: "5rem",
                        display: "flex",
                        align_items: "center",
                        justify_content: "center",

                        if let Some(profile) = current_match() {
                            "{profile.display_name}"
                        } else {
                            "No match loaded"
                        }
                    }
                }

                TabContent { index: 1usize, value: "tab2".to_string(),
                    div {
                        width: "100%",
                        height: "5rem",
                        display: "flex",
                        align_items: "center",
                        justify_content: "center",

                        if let Some(profile) = current_match() {
                            "{profile.zodiac}"
                        } else {
                            "No match loaded"
                        }
                    }
                }

                TabContent { index: 2usize, value: "tab3".to_string(),
                    div {
                        width: "100%",
                        height: "5rem",
                        display: "flex",
                        align_items: "center",
                        justify_content: "center",

                        if let Some(profile) = current_match() {
                            "{profile.bio}"
                        } else {
                            "No match loaded"
                        }
                    }
                }
            }

            div {
                style: "display: flex; gap: 0.5rem; margin-top: 1rem;",

                Button {
                    variant: ButtonVariant::Primary,
                    r#type: "button",
                    disabled: index() <= 0 || loading(),

                    onclick: move |_| async move {
                        let new_index = index() - 1;

                        loading.set(true);
                        error.set(None);

                        let result = get_matches(profile_id, new_index).await;

                        loading.set(false);

                        match result {
                            Ok(profile) => {
                                index.set(new_index);
                                current_match.set(Some(profile));
                            }
                            Err(err) => {
                                error.set(Some(format!("Could not load previous match: {err}")));
                            }
                        }
                    },

                    "Previous"
                }

                Button {
                    variant: ButtonVariant::Primary,
                    r#type: "button",
                    disabled: loading(),

                    onclick: move |_| async move {
                        let new_index = index() + 1;

                        loading.set(true);
                        error.set(None);

                        let result = get_matches(profile_id, new_index).await;

                        loading.set(false);

                        match result {
                            Ok(profile) => {
                                index.set(new_index);
                                current_match.set(Some(profile));
                            }
                            Err(err) => {
                                error.set(Some(format!("Could not load next match: {err}")));
                            }
                        }
                    },

                    "Next"
                }
            }

            if loading() {
                p {
                    style: "font-size: 0.875rem;",
                    "Loading..."
                }
            }

            if let Some(message) = error() {
                p {
                    style: "color: red; font-size: 0.875rem;",
                    "{message}"
                }
            }
        }
    }
}
