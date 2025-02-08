// static/src/js/main.js
import { mount } from 'owl';
import OwlButton from './button_component';

// Form view ke andar button ko render karna
const buttonElement = document.querySelector('#owl_button');
if (buttonElement) {
    mount(OwlButton, { target: buttonElement });
}
