import React, { Component } from 'react';
import './App.css';
import 'semantic-ui-css/semantic.min.css';
import { Container, Menu, Divider } from 'semantic-ui-react';
import { BrowserRouter, Route, Link, Switch, Redirect } from 'react-router-dom';
import PhotosPage from './photos';
import PeoplePage from './people';


class App extends Component {

  render() {
    return (
      <BrowserRouter>
        <div>
          <Menu fixed='top' inverted>
            <Container>
              <Menu.Item as='a' header><Link to='/'>A P M S</Link></Menu.Item>
              <Menu.Item as='a'><Link to='/photos'>Photos</Link></Menu.Item>
              <Menu.Item as='a'><Link to='/people'>People</Link></Menu.Item>
            </Container>
          </Menu>

          <Divider hidden />
          <Divider hidden />

          <Container>
            <Switch>
              <Redirect exact from='/' to='/photos'/>
              <Route path='/photos' component={PhotosPage} />
              <Route path='/people' component={PeoplePage} />
            </Switch>
          </Container>
        </div>
      </BrowserRouter>
    );
  }

}

export default App;
