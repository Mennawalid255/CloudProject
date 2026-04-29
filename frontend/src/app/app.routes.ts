import { Routes } from '@angular/router';
import { LoginComponent } from './login/login';
import { SignupComponent } from './signup/signup';
import { ProfileComponent } from './profile/profile';
import { EditComponent } from './edit/edit';
import { HomeComponent } from './home/home';
import { Results } from './pages/results/results';

export const routes: Routes = [
 { path: '', component: LoginComponent },
// //   { path: 'shop', component: ShopComponent },
  { path: 'login', component: LoginComponent },
  { path: 'profile', component: ProfileComponent },
  { path: 'signup', component: SignupComponent }, 
  { path: 'edit', component: EditComponent },
  {path: 'home', component: HomeComponent},
  {path: 'results', component: Results}
];