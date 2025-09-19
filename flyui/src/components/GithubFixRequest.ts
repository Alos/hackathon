        import { LitElement, css, html } from 'lit';
        // Load Lit decorators
        import { property, customElement } from 'lit/decorators.js';

        /**
         * A Lit web component that provides a UI for sending a GitHub fix request.
         * It sends the user's message to a /user-request endpoint.
         * * This version is written using TypeScript syntax and decorators.
         */
        @customElement('github-fix-request')
        export class GithubFixRequest extends LitElement {

            // --- Properties ---
            // 'requestText' is a public property, reflected as an attribute.
            @property({ type: String })
            requestText: string = '';

            // 'statusMessage' and 'isLoading' are internal component state.
            // 'state: true' means they will trigger a re-render on change,
            // but they are not configured as public attributes.
            @property({ state: true })
            statusMessage: string = '';

            @property({ state: true })
            isLoading: boolean = false;

            // --- Styles ---
            // (Styles are identical to the previous version)
            static styles = css`
                :host {
                    display: block;
                    max-width: 500px;
                    width: 100%;
                    margin: 2rem;
                    background-color: white;
                    border-radius: 0.75rem; /* 12px */
                    box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
                    overflow: hidden;
                    font-family: inherit; /* Inherit font from body */
                    box-sizing: border-box;
                }

                .container {
                    padding: 1.5rem; /* 24px */
                }

                h2 {
                    font-size: 1.5rem; /* 24px */
                    line-height: 2rem; /* 32px */
                    font-weight: 700;
                    color: rgb(31, 41, 55);
                    margin-top: 0;
                    margin-bottom: 1rem; /* 16px */
                }

                .description {
                    color: rgb(75, 85, 99);
                    margin-bottom: 1rem; /* 16px */
                    margin-top: 0;
                }

                .textarea-container {
                    margin-bottom: 1rem; /* 16px */
                }

                textarea {
                    width: 100%;
                    height: 10rem; /* 160px */
                    padding: 0.75rem; /* 12px */
                    border: 1px solid rgb(209, 213, 219);
                    border-radius: 0.5rem; /* 8px */
                    box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
                    transition: border-color 0.2s, box-shadow 0.2s;
                    box-sizing: border-box; /* Include padding in width */
                    font-family: inherit;
                    font-size: 1rem;
                }

                textarea:focus {
                    outline: none;
                    border-color: transparent;
                    box-shadow: 0 0 0 2px rgb(59, 130, 246);
                }

                textarea:disabled {
                    background-color: #f3f4f6;
                    cursor: not-allowed;
                    opacity: 0.7;
                }

                .controls {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    flex-wrap: wrap; /* Allow wrapping on small screens */
                    gap: 1rem; /* Add gap for spacing */
                }

                button {
                    padding: 0.5rem 1.5rem; /* 8px 24px */
                    background-color: rgb(37, 99, 235);
                    color: white;
                    font-weight: 600;
                    font-size: 0.875rem;
                    border-radius: 0.5rem; /* 8px */
                    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
                    border: none;
                    cursor: pointer;
                    transition: background-color 0.2s, opacity 0.2s;
                }

                button:hover:not(:disabled) {
                    background-color: rgb(29, 78, 216);
                }

                button:focus {
                    outline: none;
                    box-shadow: 0 0 0 2px rgb(59 130 246 / 0.75);
                }

                button:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }

                .status-message {
                    font-size: 0.875rem; /* 14px */
                    line-height: 1.25rem; /* 20px */
                    font-weight: 500;
                    margin: 0; /* Remove default p margin */
                }

                .status-success {
                    color: #15803d; /* text-green-700 */
                }

                .status-error {
                    color: #b91c1c; /* text-red-700 */
                }

                .status-sending {
                    color: #1d4ed8; /* text-blue-700 */
                }
            `;

            // No constructor needed as properties are initialized with defaults.

            // --- Event Handlers ---
            _handleInput(e: Event) {
                // We add a type assertion to tell TS what kind of element this is
                const target = e.target as HTMLTextAreaElement;
                this.requestText = target.value;
            }

            async _sendRequest() {
                if (this.isLoading) return;

                this.isLoading = true;
                this.statusMessage = 'Sending request...';

                try {
                    const response = await fetch('/user-request', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: this.requestText,
                        }),
                    });

                    if (response.ok) {
                        this.statusMessage = 'Request sent successfully!';
                        this.requestText = '';

                        setTimeout(() => {
                            if (this.statusMessage === 'Request sent successfully!') {
                                this.statusMessage = '';
                            }
                        }, 3000);

                    } else {
                        let errorMsg = `Error: ${response.status} - ${response.statusText}`;
                        try {
                            const errorData = await response.json();
                            errorMsg = `Error: ${response.status} - ${errorData.message || 'Server error'}`;
                        } catch (jsonError) {
                            // Could not parse JSON, stick with statusText
                        }
                        this.statusMessage = errorMsg;
                    }

                } catch (error) {
                    console.error('Fetch error:', error);
                    this.statusMessage = 'Network error. Please try again.';
                } finally {
                    this.isLoading = false;
                }
            }

            // --- Render Method ---
            render() {
                let statusClass = 'status-message';
                if (this.isLoading) {
                    statusClass += ' status-sending';
                } else if (this.statusMessage.startsWith('Error') || this.statusMessage.startsWith('Network')) {
                    statusClass += ' status-error';
                } else if (this.statusMessage) {
                    statusClass += ' status-success';
                }

                return html`
                    <div class="container">
                        <h2>
                            Submit a Fix Request
                        </h2>
                        <p class="description">
                            Describe the issue or fix you'd like to request for this GitHub repository.
                        </p>

                        <div class="textarea-container">
                            <textarea
                                placeholder="E.g., 'The login button is broken on the staging branch...'"
                                .value=${this.requestText}
                                @input=${this._handleInput}
                                ?disabled=${this.isLoading}
                            ></textarea>
                        </div>

                        <div class="controls">
                            <button
                                @click=${this._sendRequest}
                                ?disabled=${this.isLoading || this.requestText.trim() === ''}
                            >
                                ${this.isLoading ? 'Sending...' : 'Send Request'}
                            </button>

                            <!-- Display the status message -->
                            ${this.statusMessage ? html`
                                <p class="${statusClass}">
                                    ${this.statusMessage}
                                </p>
                            ` : ''}
                        </div>
                    </div>
                `;
            }
        }
