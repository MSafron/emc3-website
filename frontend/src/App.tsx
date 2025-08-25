import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Header } from '@/components/common/Header';
import { Footer } from '@/components/common/Footer';
import { HomePage } from '@/pages/HomePage';
import { CatalogPage } from '@/pages/CatalogPage';
import { ProductPage } from '@/pages/ProductPage';
import { CartPage } from '@/pages/CartPage';
import { LoginPage } from '@/pages/LoginPage';
import { ProfilePage } from '@/pages/ProfilePage';
import { ROUTES } from '@/utils/constants';

function App() {
  return (
    <div className="min-h-screen flex flex-col bg-neutral-50">
      <Header />
      
      <main className="flex-1">
        <Routes>
          <Route path={ROUTES.HOME} element={<HomePage />} />
          <Route path={ROUTES.CATALOG} element={<CatalogPage />} />
          <Route path={`${ROUTES.PRODUCT}/:id`} element={<ProductPage />} />
          <Route path={ROUTES.CART} element={<CartPage />} />
          <Route path={ROUTES.LOGIN} element={<LoginPage />} />
          <Route path={ROUTES.PROFILE} element={<ProfilePage />} />
          <Route 
            path="*" 
            element={
              <div className="container-custom py-16 text-center">
                <h1 className="text-4xl font-bold text-neutral-900 mb-4">
                  404 - Страница не найдена
                </h1>
                <p className="text-neutral-600 mb-8">
                  Запрашиваемая страница не существует или была перемещена.
                </p>
                <a 
                  href={ROUTES.HOME}
                  className="btn-primary"
                >
                  Вернуться на главную
                </a>
              </div>
            } 
          />
        </Routes>
      </main>
      
      <Footer />
    </div>
  );
}

export default App;