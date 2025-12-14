# React

React is a JavaScript library for building User Interfaces. Developed and open sourced by Facebook in 2013. It allows devs to describe what they want the UI to look like, and lets React handle how to update the UI when underlying data changes.

## Components

Building blocks of all React Apps. They're independent pieces of the UI and infinitely reusable.

- Buttons
- Inputs
- Pages

They return JSX, which is a syntax that looks like HTML but is written inside JavaScript. It provides a clear and concise way to structure UI components, making code easier to read and understand. It turns static HTML into dynamic content.

If you need a component to change its data, you should use state instead.

Controlled components use State objects to have more predictable behavior. If we want to change component's behavior now, we just have to change the state.

Pure React components mean the same input should always return the same content, and never change any other objects or variables while rendering. Strict mode tells you about mistakes you're making to prevent errors later on in production.

## Props

Props are short for properties, they are used to pass data from parent components to child components. Props make components reusable and dynamic by allowing you to customize their behavior or appearance.

```jsx
function Greeting(props) {
  return <h1>Hello, {props.name}!</h1>;
}

function App() {
  return <Greeting name="Alice" />;
}
```

- Use props in components that don’t maintain internal state.

## State

State is a snapshot of the App at any given time.

- Can't use Javascript variables because they're static
- Instead have to use special functions like `useState()` and `useReducer()`
- The useState Hook accepts a state variable (`likes`), a function to update that state variable (`setLikes`), and its starting value (`0`)
- `const [likes, setLikes] - useState()`

## Hooks

Hooks allow you to hook into features such as state within function components.

- `useState()`
- `useRef()`
- `useEffect()`
- `useReducer()`
- `useContext()`
- The first 3 ones here are the most common

## Effects

Effects are code that reach outside of React Apps, such as making an HTTP request to some other server or doing a network / database call

- These run via `useEffect()`

## Portals

Portals let you move React components into any HTML element you select.

- They're great for components that can't be displayed properly because of their parent component styles
- Use via `createPortal()` function

## Suspense

Great for components that have to wait to fetch some data. These will allow you to display some fallback component until the data is fetched nad you can display the correct content

- Ex. loading spinners
- Also great for lazy loading stuff, aka show something fake until you really need to render something

## Error Boundaries

Error boundaries can be used as fall back components whenever errors pop up. If you have a component that might error out, you can add this boundary to display some error content to the user without the entire app crashing.

## Rendering

React uses a Virtual DOM to optimize rendering performance.

- DOM stands for Document Object Model
- As users click things on a React App, React updates the Virtual DOM first and calculates minimal changes needed, and then applies them to the real DOM

The process looks like below:

1. Has State changed? If so, update the vDOM
2. If vDom has changed, run a differential check to see what's changed
3. Execute the reconciliation to update the real DOM with the changes it found
