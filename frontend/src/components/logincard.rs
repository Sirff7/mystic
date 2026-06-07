use crate::api::models::{LoginRequest, SignupRequest};
use crate::components::button::{Button, ButtonVariant};
use crate::components::card::*;
use crate::components::input::Input;
use crate::components::label::Label;
use dioxus::prelude::*;
use dioxus_router::navigator;

async fn login(email: String, password: String) -> Result<(), reqwest::Error> {
    reqwest::Client::new()
        .post("http://localhost:8000/sessions")
        .fetch_credentials_include()
        .json(&LoginRequest { email, password })
        .send()
        .await?
        .error_for_status()?;

    Ok(())
}

async fn signup(email: String, password: String) -> Result<(), reqwest::Error> {
    reqwest::Client::new()
        .post("http://localhost:8000/users")
        .json(&SignupRequest { email, password })
        .send()
        .await?
        .error_for_status()?;
    Ok(())
}

#[component]
pub fn Logincard() -> Element {
    let mut email = use_signal(String::new);
    let mut password = use_signal(String::new);
    let mut error = use_signal(|| None::<String>);
    let mut loading = use_signal(|| false);
    let nav = navigator();

    rsx! {
        Card { style: "width: 100%; max-width: 24rem;",
            CardHeader {
                CardTitle { "Login to your account" }
            }
            CardContent {
                div { style: "display: flex; flex-direction: column; gap: 1.5rem;",
                    div { style: "display: grid; gap: 0.5rem;",
                        Label { html_for: "email", "Email" }
                        Input {
                            id: "email",
                            name: "email",
                            r#type: "email",
                            placeholder: "m@example.com",
                            value: "{email}",
                            oninput: move |event: Event<FormData>| {
                                email.set(event.value());
                            }
                        }
                    }
                    div { style: "display: grid; gap: 0.5rem;",
                        div { style: "display: flex; align-items: center;",
                            Label { html_for: "password", "Password" }
                            a {
                                href: "#",
                                style: "margin-left: auto; font-size: 0.875rem; color: var(--secondary-color-5); text-decoration: underline; text-underline-offset: 4px;",
                                "Forgot your password?"
                            }
                        }
                        Input {
                            id: "password",
                            name: "password",
                            r#type: "password",
                            value: "{password}",
                            oninput: move |event: Event<FormData>| {
                                password.set(event.value());
                            }
                        }
                    }
                    if let Some(message) = error() {
                        p { style: "color: red; font-size: 0.875rem;", "{message}" }
                    }
                }
            }
            CardFooter { style: "flex-direction: column; gap: 0.5rem;",
                Button {
                    variant: ButtonVariant::Outline,
                    r#type: "button",
                    style: "width: 100%;",

                    onclick: move |_| async move {
                        loading.set(true);
                        error.set(None);

                        let result = login(email(), password()).await;

                        loading.set(false);

                        match result {
                            Ok(_) => {
                                nav.push("/discover");
                            }
                            Err(err) => {
                                error.set(Some(format!("Signup failed: {err}")));
                            }
                        }
                    }, "Login"
                }
                Button {
                    variant: ButtonVariant::Outline,
                    r#type: "button",
                    style: "width: 100%;",

                    onclick: move |_| async move {
                        loading.set(true);
                        error.set(None);

                        let result = signup(email(), password()).await;

                        loading.set(false);

                        match result {
                            Ok(_) => {
                                nav.push("/discover");
                            }
                            Err(err) => {
                                error.set(Some(format!("Signup failed: {err}")));
                            }
                        }
                    },

                    "Sign up"
                }
            }
        }
    }
}
