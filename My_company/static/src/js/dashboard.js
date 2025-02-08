// static/src/js/button_component.js
import { Component, useState } from 'owl';
import { xml } from '@odoo/owl';  // Import xml for the template

class OwlButton extends Component {
    setup() {
        // Define the state for the button text
        this.state = useState({ buttonText: 'Click Me!' });
    }

    // Define what happens when the button is clicked
    onClick() {
        this.state.buttonText = 'Clicked!';
        alert("Button Clicked!");
    }

    // Template for the button, using Owl's template syntax
    static template = xml`
        <button t-on-click="onClick" class="btn btn-primary">
            <t t-esc="state.buttonText"/>
        </button>
    `;
}

export default OwlButton;
